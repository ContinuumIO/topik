from __future__ import absolute_import, print_function

import json
import os
import logging
import gzip
import solr
import requests
import time
import pdb
from elasticsearch import Elasticsearch, helpers


from topik.utils import batch_concat

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



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
    """
    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                dictionary = {}
                dictionary['_source'] = json.loads(line)
                # should we check to see whether there are any existing document
                # attributes called 'filename'?
                if year_field:
                    dictionary['_source'][year_field] = int(dictionary['_source'][year_field])
                dictionary['_source']['filename'] = filename
                if id_field:
                    dictionary['_id'] = dictionary['_source'][id_field]
                else:
                    dictionary['_id'] = n
                yield dictionary
            except ValueError:
                logging.warning("Unable to process line: %s" %
                                str(line))
    """
    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                dictionary = {}
                dictionary = json.loads(line)
                yield dict_to_doc(dictionary, year_field, id_field)
            except ValueError:
                logging.warning("Unable to process line: %s" %
                                str(line))

def iter_elastic_dump(filename, year_field=None, id_field=None, item_prefix='item'):

    from ijson import items

    with open(filename, 'r') as f:
        for item in items(f, item_prefix):
            if type(item) == dict:
                yield dict_to_doc(item, year_field=year_field, id_field=id_field)
            elif type(item) == list:
                for sub_item in item:
                    if type(sub_item) ==  dict:
                        yield dict_to_doc(sub_item, year_field=year_field, id_field=id_field)



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
    """
    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(files):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    dictionary = {}
                    dictionary['_source'] = {}
                    dictionary['_source']['filename'] = fullpath
                    dictionary['_id'] = n
                    dictionary['_source'][content_field] = f.read().decode('utf-8')
                    #pdb.set_trace()
                    yield dictionary
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)
    """
    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(files):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    dictionary = {}
                    fields = [(content_field    , f.read().decode('utf-8')),
                              (filename         , fullpath)]

                    yield dict_to_doc(dictionary, addtl_fields=fields)
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)

'''
def iter_large_json(json_file, prefix_value, event_value):
    import ijson

    parser = ijson.parse(open(json_file))

    for prefix, event, value in parser:
        # For Flowdock data ('item.content', 'string')
        if (prefix, event) == (prefix_value, event_value):
            yield "%s/%s" % (prefix, event), value

'''
def iter_large_json(json_file, prefix_value, event_value):
    import ijson
    
    parser = ijson.parse(open(json_file))
    
    for prefix, event, value in parser:
        # For Flowdock data ('item.content', 'string')
        #print('%r|%r|%r' % (prefix, event, value))
        #pdb.set_trace()
        if (prefix, event) == (prefix_value, event_value):
            yield "%s/%s" % (prefix, event), value


def iter_solr_query(solr_instance, field, query="*:*"):
    s = solr.SolrConnection(solr_instance)
    response = s.query(query)
    return batch_concat(response, field,  content_in_list=False)


def iter_elastic_query(instance, index, field, subfield=None):
    es = Elasticsearch(instance)

    # initial search
    resp = es.search(index, body={"query": {"match_all": {}}}, scroll='5m')

    scroll_id = resp.get('_scroll_id')
    if scroll_id is None:
        return

    first_run = True
    while True:
        for hit in resp['hits']['hits']:
            s = hit['_source']
            try:
                if subfield is not None:
                    yield "%s/%s" % (field, subfield), s[field][subfield]
                else:
                    yield field, s[field]
            except ValueError:
                    logging.warning("Unable to process row: %s" %
                                    str(hit))

        scroll_id = resp.get('_scroll_id')
        # end of scroll
        if scroll_id is None or not resp['hits']['hits']:
            break

"""
===================================================================
STEP 1.5: Conform dict to elasticsearch standard document structure
===================================================================
"""

def dict_to_doc(dictionary, year_field=None, id_field=None, addtl_fields=None):
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

    print(bulk_index)
    pre_clock = time.clock()
    number_of_docs_pushed_to_bulk = bulk_index[0]
    number_of_docs_in_index = -1
    while number_of_docs_pushed_to_bulk != number_of_docs_in_index:
        r = requests.get('http://localhost:9200/_cat/indices?v')
        rlist = r.text.split()
        number_of_docs_in_index = int(rlist[rlist.index(index)+ 3])
        print("Number of documents in the index '%s': " % index, end="")
        print(number_of_docs_in_index)
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
    else:
        results = helpers.scan(client=es, index=index, scroll='5m')

    for result in results:
        if content_field in result['_source'].keys():
            yield result['_source'][content_field]




