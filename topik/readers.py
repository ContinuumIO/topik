from __future__ import absolute_import, print_function

from collections import Iterable
import gzip
import json
import logging
import os
import time

from elasticsearch import Elasticsearch, helpers
from ijson import items
import requests
import solr

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

"""
====================================================================
STEP 1: Read all documents from source and yield full-featured dicts
====================================================================
"""

def iter_document_json_stream(filename, content_field, year_field):
    """Iterate over a json stream of items and get the field that contains the text to process and tokenize.

    Parameters
    ----------
    filename: string
        The filename of the json stream.

    content_field: string
        The name fo the field that contains the main text body of the document.

    year_field: string
        The field name (if any) that contains the year associated with the document.

    $ head -n 2 ./tests/data/test_data_json_stream_2.json
        {"topic": "interstellar film review", "text": "'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one of the most original I've seen in a while.", "id": 1, "year": 1998}
        {"topic": "big data", "text": "Big Data are becoming a new technology focus both in science and in industry and motivate technology shift to data centric architecture and operational models.", "id": 2, "year": 1999}
    >>> documents = iter_document_json_stream('./topik/tests/data/test_data_json_stream_2.json', "text", "year")
    >>> next(documents) == {'_id': -7625602235157556658,
    ...     '_source': {'filename': './topik/tests/data/test_data_json_stream_2.json', u'id': 1,
    ...                 u'text': u"'Interstellar' was incredible. The visuals, the score, the acting, " +
    ...                          u"were all amazing. The plot is definitely one of the most original " +
    ...                          u"I've seen in a while.",
    ...                 u'topic': u'interstellar film review',
    ...                 u'year': 1998}}
    True
    """

    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                dictionary = {}
                dictionary = json.loads(line)
                yield dict_to_es_doc(dictionary, content_field=content_field, year_field=year_field, addtl_fields=[('filename', filename)])
            except ValueError:
                logging.warning("Unable to process line: %s" %
                                 str(line))

def iter_large_json(filename, content_field, year_field, item_prefix='item'):
    """Iterate over all items and sub-items in a json object that match the specified prefix


    Parameters
    ----------
    filename: string
        The filename of the large json file

    content_field: string
        The name fo the field that contains the main text body of the document.

    year_field: string
        The field name (if any) that contains the year associated with the document

    item_prefix: string
        The string representation of the hierarchical prefix where the items of 
        interest may be located within the larger json object.

        Try the following script if you need help determining the desired prefix:
        $   import ijson
        $       with open('test-data_large-json-2.json', 'r') as f:
        $           parser = ijson.parse(f)
        $           for prefix, event, value in parser:
        $               print("prefix = '%r' || event = '%r' || value = '%r'" %
        $                     (prefix, event, value))

    >>> documents = iter_large_json('./topik/tests/data/test_data_large_json_2.json', 'text', 'year')
    >>> next(documents) == {'_id': -7625602235157556658, '_source': {u'topic': u'interstellar film review', 
    ...                     u'text': u"'Interstellar' was incredible. The visuals, the score, the acting, " +
    ...                              u"were all amazing. The plot is definitely one of the most original I've " +
    ...                              u"seen in a while.", 
    ...                     u'id': 1, u'year': 1998,
    ...                     'filename': './topik/tests/data/test_data_large_json_2.json'}}
    True

    """
    with open(filename, 'r') as f:
        for item in items(f, item_prefix):
            if hasattr(item, 'keys') and content_field in item: # check if item is a dictionary
                yield dict_to_es_doc(item, content_field=content_field, year_field=year_field, addtl_fields=[('filename', filename)])
            elif isinstance(item, Iterable) and not isinstance(item, str): # check if item is both iterable and not a string
                for sub_item in item:
                    if hasattr(sub_item, 'keys') and content_field in sub_item: # check if sub_item is a dictionary
                        yield dict_to_es_doc(sub_item, content_field=content_field, year_field=year_field, addtl_fields=[('filename', filename)])
            else:
                raise ValueError("'item' in json source is not a dict, and is either a string or not iterable: %r" % item)


def iter_documents_folder(folder, content_field='text', year_field='year'):
    """Iterate over the files in a folder to retrieve the content to process and tokenize.

    Parameters
    ----------
    folder: string
        The folder containing the files you want to analyze.

    content_field: string
        The name fo the field that contains the main text body of the document.

    year_field: string
        The field name (if any) that contains the year associated with the document

    $ ls ./topik/tests/data/test_data_folder_files
        doc1  doc2  doc3
    >>> documents = iter_documents_folder('./topik/tests/data/test_data_folder_files')
    >>> next(documents) == {'_id': -7625602235157556658, '_source': {
    ...     'text': u"'Interstellar' was incredible. The visuals, the score, " +
    ...             u"the acting, were all amazing. The plot is definitely one " +
    ...             u"of the most original I've seen in a while.", 
    ...     'filename': './topik/tests/data/test_data_folder_files/doc1', 'year': -1}}
    True

    [u"'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one
    of the most original I've seen in a while."]
    """
    if not os.path.exists(folder):
        raise IOError("Folder not found!")
    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(files):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    dictionary = {}
                    dictionary[content_field] = f.read().decode('utf-8')
                    fields = [('filename'       , fullpath)]
                    yield dict_to_es_doc(dictionary, content_field=content_field, 
                                         year_field=year_field, 
                                         addtl_fields=fields)
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)

def iter_solr_query(solr_instance, content_field, year_field, query="*:*", content_in_list=True):
    """Iterate over all documents in the specified solr intance that match the specified query

    Parameters
    ----------
    solr_instance: string
        Address of the solr instance

    content_field: string
        The name fo the field that contains the main text body of the document.

    year_field: string
        The field name (if any) that contains the year associated with the document

    query: string
        The solr query string

    content_in_list: bool
        Whether the source fields are stored in single-element lists.  Used for unpacking.
    """
    s = solr.SolrConnection(solr_instance)
    results_per_batch = 100
    response = s.select(query, rows=results_per_batch)
    while response.results:
        for item in response.results:
            if content_in_list:
                if content_field in item.keys() and type(item[content_field]) == list:
                    item[content_field] = item[content_field][0]
                if year_field in item.keys() and type(item[year_field]) == list:
                    item[year_field] = item[year_field][0]
            yield item
        response = response.next_batch()

def iter_elastic_query(es_full_path, content_field, year_field, query):
    """Iterate over all documents in the specified elasticsearch intance and index that match the specified query

    Parameters
    ----------
    instance: string
        Address of the elasticsearch instance including index

    query: string
        The solr query string

    content_field: string
        The name fo the field that contains the main text body of the document.

    year_field: string
        The field name (if any) that contains the year associated with the document
    """

    if es_full_path[-1] == '/':
        es_full_path = es_full_path[:-1]
    instance, index = es_full_path.rsplit('/',1)

    es = Elasticsearch(instance)

    results = helpers.scan(client=es, index=index, scroll='5m', query=query)

    for result in results:
        yield dict_to_es_doc(result['_source'], content_field, year_field)

"""
===================================================================
STEP 1.5: Conform dict to elasticsearch standard document structure
===================================================================
"""

def dict_to_es_doc(dictionary, content_field, year_field, addtl_fields=None):
    """Convert a dictionary to one that is formatted as a standard elasticsearch document

    Parameters
    ----------
    dictionary: dict
        The source document (in dict form) to be converted to a standard elasticsearch document dictionary

    content_field: string
        The name fo the field that contains the main text body of the document.

    year_field: string
        The field name (if any) that contains the year associated with the document

    addtl_fields: list of tuple, where each tuple is a (key, value) pair
        These are additional fields to be added to the es-formatted dict, whose values are known upon reading from source.
    
    >>> d = {u'id': 1,
    ...      u'text': u"'Interstellar' was incredible. The visuals, the score, the acting, " +
    ...               u"were all amazing. The plot is definitely one of the most original " +
    ...               u"I've seen in a while.",
    ...      u'topic': u'interstellar film review',
    ...      u'year': '1998'}
    >>> es_doc = dict_to_es_doc(d, 'text', 'year', [('filename', './tests/data/test-data_json-stream-2.json')])
    >>> es_doc == {'_id': -7625602235157556658,
    ...     '_source': {'filename': './tests/data/test-data_json-stream-2.json', u'id': 1,
    ...                 u'text': u"'Interstellar' was incredible. The visuals, the score, the acting, " +
    ...                          u"were all amazing. The plot is definitely one of the most original " +
    ...                          u"I've seen in a while.",
    ...                 u'topic': u'interstellar film review',
    ...                 u'year': 1998}}
    True
    """
    es_doc_dict = {}
    es_doc_dict['_source'] = dictionary
    if year_field:
        try:
            # TODO: replace 'int()' with some sort of 'extract_year()' to accept more formats
            es_doc_dict['_source'][year_field] = int(es_doc_dict['_source'][year_field])
        except (ValueError, KeyError) as err:
            es_doc_dict['_source'][year_field] = -1
    if content_field and content_field in dictionary.keys():
        es_doc_dict['_id'] = hash(dictionary[content_field])
    else:
        raise ValueError("Invalid value for 'content_field'")
    if addtl_fields:
        for key, value in addtl_fields:
            es_doc_dict['_source'][key] = value
    return es_doc_dict

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

    number_of_docs_in_index = -1

    while es.count(index=index, doc_type=doc_type)['count'] != number_of_docs_in_index:
        number_of_docs_in_index = es.count(index=index, doc_type=doc_type)['count']
        time.sleep(1)
        logging.info("Number of documents in the index '%s': %d" % (index, number_of_docs_in_index))
            
    logging.info("%d documents successfully indexed" % number_of_docs_in_index)
        
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




