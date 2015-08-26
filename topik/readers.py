from __future__ import absolute_import, print_function

import gzip
import json
import logging
import os
import time

from elasticsearch import Elasticsearch, helpers
from ijson import items
import requests
import solr

from topik.utils import batch_concat

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

"""
====================================================================
STEP 1: Read all documents from source and yield full-featured dicts
====================================================================
"""

def iter_document_json_stream(filename, year_field, id_field):
    """Iterate over a json stream of items and get the field that contains the text to process and tokenize.

    Parameters
    ----------
    filename: string
        The filename of the json stream.

    year_field: string
        The field name (if any) that contains the year associated with the document

    $ head -n 2 ./topik/tests/data/test-data-1
        {"id": 1, "topic": "interstellar film review", "text":"'Interstellar' was incredible. The visuals, the score..."}
        {"id": 2, "topic": "big data", "text": "Big Data are becoming a new technology focus both in science and in..."}
    >>> document = iter_document_json_stream('./topik/tests/test-data-1.json', "text")
    >>> next(document)
    {'_id': 0,
     '_source': {'filename': './topik/tests/data/test-data-3.json',
      u'id': 1,
      u'text': u"'Interstellar' was incredible. The visuals, the score, the acting, 
                  were all amazing. The plot is definitely one of the most original 
                  I've seen in a while.",
      u'topic': u'interstellar film review',
      u'year': 1998}}
    """

    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                dictionary = {}
                dictionary = json.loads(line)
                yield dict_to_es_doc(dictionary, year_field, id_field)
            except ValueError:
                logging.warning("Unable to process line: %s" %
                                str(line))

def iter_large_json(filename, year_field, id_field, item_prefix='item'):
    """Iterate over all items and sub-items in a json object that match the specified prefix"""
    with open(filename, 'r') as f:
        for item in items(f, item_prefix):
            if hasattr(item, 'keys'): # check if item is a dictionary
                yield dict_to_es_doc(item, year_field=year_field, id_field=id_field)
            elif isinstance(item, Iterable) and not isinstance(item, str): # check if item is both iterable and not a string
                for sub_item in item:
                    if hasattr(sub_item, 'keys'): # check if sub_item is a dictionary
                        yield dict_to_es_doc(sub_item, year_field=year_field, id_field=id_field)
            else:
                raise ValueError("'item' in json source is not a dict, and is either a string or not iterable: %r" % item)


def iter_documents_folder(folder, content_field='text', year_field='year'):
    """Iterate over the files in a folder to retrieve the content to process and tokenize.

    Parameters
    ----------
    folder: string
        The folder containing the files you want to analyze.

    $ ls ./topik/tests/test-data-folder
        doc1  doc2  doc3
    >>> doc_text = iter_documents_folder('./topik/tests/test-data-1.json')
    >>> fullpath, content = next(doc_text)
    >>> content
    [u"'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one
    of the most original I've seen in a while."]
    """

    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(files):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    dictionary = {}
                    fields = [(content_field    , f.read().decode('utf-8')),
                              ('filename'       , fullpath),
                              (year_field       , 'N/A')]

                    yield dict_to_es_doc(dictionary, addtl_fields=fields)
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)


def iter_solr_query(solr_instance, field, query="*:*"):
    """Iterate over all documents in the specified solr intance that match the specified query"""
    s = solr.SolrConnection(solr_instance)
    response = s.query(query)
    return batch_concat(response, field,  content_in_list=False)


def iter_elastic_query(instance, index, query, year_field, id_field):
    """Iterate over all documents in the specified elasticsearch intance and index that match the specified query"""
    es = Elasticsearch(instance)

    results = helpers.scan(client=es, index=index, scroll='5m', query=query)

    for result in results:
        yield dict_to_es_doc(result['_source'], year_field, id_field)

"""
===================================================================
STEP 1.5: Conform dict to elasticsearch standard document structure
===================================================================
"""
# TODO: generate the _id by hashing content field, always (take away the option for them to do it).  Also means content_field needs to be an input here.
def dict_to_es_doc(dictionary, year_field, id_field, addtl_fields=None):
    """Convert a dictionary to one that is formatted as a standard elasticsearch document"""
    doc_dict = {}
    doc_dict['_source'] = dictionary
    if year_field:
        if year_field in dictionary.keys():
            doc_dict['_source'][year_field] = int(doc_dict['_source'][year_field])
    if id_field and id_field in dictionary.keys():
        doc_dict['_id'] = dictionary[id_field]
    if addtl_fields:
        for key, value in addtl_fields:
            doc_dict['_source'][key] = value
    return doc_dict

"""
=============================================================
STEP 2: Load dicts from generator into elasticsearch instance
=============================================================
"""

def reader_to_elastic(instance, index, documents, clear_index, doc_type='document'):
    """Takes the generator yielded by the selected reader and iterates over it 
    to load the documents into elasticsearch"""

    es = Elasticsearch(instance)
    
    if clear_index:
        if es.indices.exists(index):
            logging.info("Index '%s' exists, so can be deleted..." % index)
            
            es.indices.delete(index)
            logging.info("Index '%s' deleted." % index)
        else:
            logging.warning("Index '%s' does not exist so cannot be deleted." % index)
            
    bulk_index = helpers.bulk(client=es, actions=documents, index=index, 
                              doc_type=doc_type)
    
    pre_clock = time.clock()
    number_of_docs_pushed_to_bulk = bulk_index[0]
    number_of_docs_in_index = es.count(index=index, doc_type=doc_type)['count']
    
    while number_of_docs_pushed_to_bulk != number_of_docs_in_index:
        time.sleep(0.1)
        number_of_docs_in_index = es.count(index=index, doc_type=doc_type)['count']
        logging.debug("Number of documents in the index '%s': %d" % (index, number_of_docs_in_index))
        if (time.clock() - pre_clock) > 10:
            break
            
    if number_of_docs_in_index == number_of_docs_pushed_to_bulk:
        logging.debug("Time it took after displaying bulk results for ES to catch up: %d" % (time.clock() - pre_clock))
        logging.info("All %d documents successfully indexed" % number_of_docs_in_index)
    elif not clear_index:
        if (number_of_docs_in_index > number_of_docs_pushed_to_bulk):
            logging.warning("Timeout reached and the number of documents in the index does not match the number bulked. This may be due to previously existing documents in the index")
            logging.info("All %r documents NOT successfully indexed" % number_of_docs_in_index)
        else:
            logging.warning("Number of documents in the index (%d) is less than the number pushed to bulk (%d)." % (number_of_docs_in_index, number_of_docs_pushed_to_bulk))
    else:
        logging.warning("Number of documents in the index (%d) is different than the number pushed to bulk (%d)." % (number_of_docs_in_index, number_of_docs_pushed_to_bulk))
        
"""
===========================================================
STEP 3: Get year-filtered documents back from elasticsearch
===========================================================
"""

def get_filtered_elastic_results(instance, index, content_field, year_field,
                                 start_year, stop_year):
    """Queries elasticsearch for all documents within the specified year range
    and returns a generator of the results"""
    es = Elasticsearch(instance)

    if year_field and (start_year or stop_year):

        results = helpers.scan(client=es, index=index, scroll='5m',
                        query={"query": 
                                {"constant_score": 
                                    {"filter":
                                        {"range":
                                            {year_field:
                                                {"gte": start_year,
                                                 "lte": stop_year}}}}}})

    else:
        results = helpers.scan(client=es, index=index, scroll='5m')

    for result in results:
        if content_field in result['_source'].keys():
            yield result['_source'][content_field]




