from __future__ import absolute_import, print_function

import json
import os
import logging
import gzip
import solr
import requests
import time
from ijson import items
from elasticsearch import Elasticsearch, helpers


from topik.utils import batch_concat

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# TODO: look for helper functions where I've defined default values, preferable not to do that so that it shows up if not defined.

"""
====================================================================
STEP 1: Read all documents from source and yield full-featured dicts
====================================================================
"""

def iter_document_json_stream(filename, year_field=None, id_field=None):
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

def iter_large_json(filename, year_field=None, id_field=None, item_prefix='item'):

    with open(filename, 'r') as f:
        for item in items(f, item_prefix):
            if hasattr(item, 'keys'):
            # TODO: if type(item) == dict:
                yield dict_to_es_doc(item, year_field=year_field, id_field=id_field)
            # TODO: elif hasattr(item, '') find some way to see that it (1) is iterable but (2) not a string
            elif type(item) == list:
                for sub_item in item:
                    if type(sub_item) ==  dict:
                        yield dict_to_es_doc(sub_item, year_field=year_field, id_field=id_field)
            #else:
            #    raise ValueError:
                    # TODO: logging.warning("") Warning: Any other objects

'''
def iter_large_json_OLD(json_file, prefix_value, event_value):
    import ijson

    parser = ijson.parse(open(json_file))

    for prefix, event, value in parser:
        # For Flowdock data ('item.content', 'string')
        if (prefix, event) == (prefix_value, event_value):
            yield "%s/%s" % (prefix, event), value

'''


def iter_documents_folder(folder, content_field='text'):
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
    # TODO: write a default year-field to some "unknown" value

    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(files):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    dictionary = {}
                    fields = [(content_field    , f.read().decode('utf-8')),
                              ('filename'       , fullpath)]

                    yield dict_to_es_doc(dictionary, addtl_fields=fields)
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)


def iter_solr_query(solr_instance, field, query="*:*"):
    s = solr.SolrConnection(solr_instance)
    response = s.query(query)
    return batch_concat(response, field,  content_in_list=False)


def iter_elastic_query(instance, index, query=None,
                       year_field=None, id_field=None):
    # TODO: add description
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
def dict_to_es_doc(dictionary, year_field=None, id_field=None, addtl_fields=None):
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

def reader_to_elastic(instance, index, documents, clear_index=False):
    """Takes the generator yeilded by the selected reader and iterates over it 
    to load the documents into elasticsearch"""
    #TODO: replace all with logging
    #TODO: es.indices.exists(es_index), es.indices.delete
    if clear_index:
        full_index_path = instance + '/' + index 
        r = requests.get(full_index_path) #Check to see if the index exists
        if r.status_code == 200:
            print("Index '%s' exists, so can be deleted..." % full_index_path)
            r = requests.delete(full_index_path)
            if r.status_code == 200:
                print("Index '%s' successfully deleted" % full_index_path)
                r = requests.get(full_index_path)
                if r.status_code != 200:
                    print("Unsuccessful request for index '%s' confirms its absence." 
                            % full_index_path)
                    r = requests.put(full_index_path)
                    if r.status_code == 200:
                        print("Index '%s' successfully recreated" % full_index_path)
                else:
                    print("Actually, deletion appears unsuccessful after all!")
            else:
                print("Problem reported with deletion request!")
        else:
            print("No index '%s' exists, so can't be deleted." % full_index_path)



    es = Elasticsearch(instance)

    bulk_index = helpers.bulk(client=es, actions=documents, index=index, 
                              doc_type='document')#, chunk_size=5000)

    # TODO: replace with logging: print(bulk_index)
    pre_clock = time.clock()
    number_of_docs_pushed_to_bulk = bulk_index[0]
    number_of_docs_in_index = -1
    # TODO: replace with api call to get document count for the index
    # full_doc_count = es.count(index=index, doc_type=doc_type)['count']
    while number_of_docs_pushed_to_bulk != number_of_docs_in_index:
        r = requests.get('http://localhost:9200/_cat/indices?v')
        rlist = r.text.split()
        number_of_docs_in_index = int(rlist[rlist.index(index)+ 3])
        print("Number of documents in the index '%s': " % index, end="")
        print(number_of_docs_in_index)
        # TODO: add timeout, and also sleep function
    # TODO: replace all prints with logging
    print("Time it took after displaying bulk results for ES to catch up: ", end="")
    print(time.clock() - pre_clock)
    print("All documents successfully indexed")

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
        # Do we need to do a check to make sure this field exists in the mapping?
        results = helpers.scan(client=es, index=index, scroll='5m',
                        query={"query": 
                                {"constant_score": 
                                    {"filter":
                                        {"range":
                                            {year_field:
                                                {"gte": start_year,
                                                 "lte": stop_year}}}}}})
    # TODO: confirm that this is necessary
    else:
        results = helpers.scan(client=es, index=index, scroll='5m')

    for result in results:
        if content_field in result['_source'].keys():
            yield result['_source'][content_field]




