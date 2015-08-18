from __future__ import absolute_import, print_function

import json
import os
import logging
import gzip
import solr
import requests
from elasticsearch import Elasticsearch, helpers


from topik.utils import batch_concat

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

"""
============================================
STEP 1: Create generator to read from source
============================================
"""

def iter_document_json_stream(filename, year_field):#, field):
    """Iterate over a json stream of items and get the field that contains the text to process and tokenize.

    Parameters
    ----------
    filename: string
        The filename of the json stream.

    field: string
        The field name that contains the text that needs to be processed

    $ head -n 2 ./topik/tests/data/test-data-1
        {"id": 1, "topic": "interstellar film review", "text":"'Interstellar' was incredible. The visuals, the score..."}
        {"id": 2, "topic": "big data", "text": "Big Data are becoming a new technology focus both in science and in..."}
    >>> document = iter_document_json_stream('./topik/tests/test-data-1.json', "text")
    >>> next(document)[1]
    [u"'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one
    of the most original I've seen in a while."]

    """
    
    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                dictionary = {}
                dictionary['_source'] = json.loads(line)
                # should we check to see whether there are any existing document
                # attributes called 'filename' or 'id'?
                dictionary['_source'][year_field] = int(dictionary['_source'][year_field])
                dictionary['_source']['filename'] = filename
                dictionary['_id'] = n
                yield dictionary
            except ValueError:
                logging.warning("Unable to process line: %s" %
                                str(line))

    """
    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                dictionary = json.loads(line)
                content = dictionary.get(field)
                id = "%s/%s[%d]" % (filename, field, n)
                yield id, content
            except ValueError:
                logging.warning("Unable to process line: %s" %
                                str(line))
    """


def iter_documents_folder(folder):
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
        for file in files:
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    yield fullpath, f.read().decode('utf-8')
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)


def iter_large_json(json_file, prefix_value, event_value):
    import ijson

    parser = ijson.parse(open(json_file))

    for prefix, event, value in parser:
        # For Flowdock data ('item.content', 'string')
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
=============================================================
STEP 2: Load dicts from generator into elasticsearch instance
=============================================================
"""

def reader_to_elastic(instance, index, documents, clear_index=False):
    """Takes the generator yeilded by the selected reader and iterates over it 
    to load the documents into elasticsearch"""
    #host, port = tuple(instance.rsplit(':', 1))
    #http://localhost:9200/top/document/101
    #{"error":"IndexMissingException[[top] missing]","status":404}
    if clear_index:
        # DELETE THE INDEX! Can I just give the delete command or do I need
        # to check for its existence first?  Do I also need to check for
        # successful deletion afterward?
        full_index_path = instance + '/' + index 
        r = requests.get(full_index_path)
        if r.status_code == 200:
            r = requests.delete(full_index_path)

    es = Elasticsearch(instance)
    #for i, document in enumerate(documents):
        #es.index(index=index, doc_type='document', body=document,
        #         id=document['id'])
    bulk_index = helpers.bulk(client=es, actions=documents, index=index, 
                              doc_type='document')
    #    print("\rIndexing Document: %d" % i, end="")
    print("\nAll documents successfully indexed")

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
    results = helpers.scan(client=es, index=index, query={"query":
    #return es.search(index=index, size=20, search_type="scan",scroll="1m",# search_type="scan"
    #                 body={
    #                       "query": 
                            {"constant_score": 
                                {"filter":
                                    {"range":
                                        {year_field:
                                            {"gte": start_year,
                                            "lte": stop_year}}}}}})
    for result in results:
        yield result['_source'][content_field]



def iter_elastic_query_JUNK(instance, index, field, subfield=None):
    #host, port = tuple(instance.split(':'))
    es = Elasticsearch(instance)

    # initial search
    #resp = es.search(index, body={"query": {"match_all": {}}}, scroll='5m')
    resp = es.search(index=index, #search_type="scan",
                     query={"query": 
                            {"constant_score": 
                                {"filter":
                                    {"range":
                                        {"year":
                                            {"gte": 1979,
                                            "lte": 1979}}}}}})#, scroll='1m')

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
        print(scroll_id)
        if scroll_id is None or not resp['hits']['hits']:
            break


def print_hits(results, facet_masks={}):
    " Simple utility function to print results of a search query. "
    print('=' * 80)
    print('Total %d found in %dms' % (results['hits']['total'], results['took']))
    if results['hits']['hits']:
        print('=' * 80)
        print("Total number of results: %d" % results['hits']['total'])
        print('-' * 80)
    for hit in results['hits']['hits']:
        # get created date for a repo and fallback to authored_date for a commit
        #created_at = parse_date(hit['_source'].get('created_at', hit['_source']['authored_date']))
        '''print('/%s/%s/%s (%s): %s' % (
                hit['_index'], hit['_type'], hit['_id'],
                created_at.strftime('%Y-%m-%d'),
                hit['_source']['description'].replace('\n', ' ')))'''
        print(hit)

    for facet, mask in facet_masks.items():
        print('-' * 80)
        for d in results['facets'][facet]['terms']:
            print(mask % d)
    print('=' * 80)
    print()



