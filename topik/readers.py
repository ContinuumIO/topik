from __future__ import absolute_import, print_function

import os
import logging

from elasticsearch import Elasticsearch, helpers

from topik.intermediaries.raw_data import output_formats

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# TODO: look for helper functions where I've defined default values, preferable not to do that so that it shows up if not defined.

"""
====================================================================
STEP 1: Read all documents from source and yield full-featured dicts
====================================================================
"""

def _iter_document_json_stream(filename, year_field=None, id_field=None, **kwargs):
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
    >>> document = _iter_document_json_stream('./topik/tests/test-data-1.json', "text")
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
    import json
    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                yield json.loads(line)
            except ValueError as e:
                logging.warning("Unable to process line: {} (error was: {})".format(str(line), e))


def _iter_large_json(filename, year_field=None, id_field=None, item_prefix='item', **kwargs):
    from ijson import items
    with open(filename, 'r') as f:
        for item in items(f, item_prefix):
            if hasattr(item, 'keys'):
            # TODO: if type(item) == dict:
                yield item
            # TODO: elif hasattr(item, '') find some way to see that it (1) is iterable but (2) not a string
            elif type(item) == list:
                for sub_item in item:
                    if type(sub_item) ==  dict:
                        yield sub_item
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


def _iter_documents_folder(folder, content_field='text', **kwargs):
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
    import gzip

    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(files):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    yield {content_field: f.read().decode('utf-8'),
                                  'filename': fullpath}
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: %s" % fullpath)


def _iter_solr_query(solr_instance, field, query="*:*", **kwargs):
    import solr
    from topik.utils import batch_concat
    s = solr.SolrConnection(solr_instance)
    response = s.query(query)
    return batch_concat(response, field,  content_in_list=False)


def _iter_elastic_query(instance, index, query=None,
                       year_field=None, id_field=None, **kwargs):
    # TODO: add description
    es = Elasticsearch(instance)

    results = helpers.scan(client=es, index=index, scroll='5m', query=query)

    for result in results:
        yield result['_source']

"""
=============================================================
STEP 2: Load dicts from generator into elasticsearch instance
=============================================================
"""

def read_input(source, content_field, source_type="auto", output_type="elasticsearch", output_args=None,
               synchronous_wait=0, **kwargs):
    import re
    import time
    json_extensions = [".js", ".json"]
    ip_regex = "/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/"
    web_regex = "^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/"
    if output_args is None:
        output_args = {}

    ip_match = re.compile(ip_regex)
    web_match = re.compile(web_regex)

    # solr defaults to port 8983
    if (source_type=="auto" and "8983" in source) or source_type == "solr":
        data_iterator = _iter_solr_query(source, **kwargs)
    # web addresses default to elasticsearch
    elif (source_type == "auto" and (ip_match.search(source) or web_match.search(source))) or source_type == "elastic":
        data_iterator = _iter_elastic_query(source, **kwargs)
    # files must end in .json.  Try json parser first, try large_json parser next.  Fail otherwise.
    elif (source_type == "auto" and os.path.splitext(source)[1] in json_extensions) or source_type == "json_stream":
        try:
            data_iterator = _iter_document_json_stream(source, **kwargs)
        except ValueError:
            data_iterator = _iter_large_json(source, **kwargs)
    elif source_type == "large_json":
        data_iterator = _iter_large_json(source, **kwargs)
    # folder paths are simple strings that don't end in an extension (.+3-4 characters), or end in a /
    elif (source_type == "auto" and os.path.splitext(source)[1] == "") or source_type == "folder":
        data_iterator = _iter_documents_folder(source, content_field=content_field)
    else:
        raise ValueError("Unrecognized source type: {}.  Please either manually specify the type, or convert your input"
                         " to a supported type.".format(source))
    output = output_formats[output_type](iterable=data_iterator, **output_args)

    if synchronous_wait > 0:
        start = time.time()
        items_stored = output.get_number_of_items_stored()
        time.sleep(1)
        while items_stored != output.get_number_of_items_stored() and time.time() - start < synchronous_wait:
            logging.debug("Number of documents added to the index: {}".format(output.get_number_of_items_stored()))
            time.sleep(3)

    return output

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




