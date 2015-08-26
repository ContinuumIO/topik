from __future__ import absolute_import, print_function

import os
import logging

from topik.intermediaries.raw_data import output_formats

# imports used only for doctests
from topik.tests import test_data_path

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def _iter_document_json_stream(filename):
    """Iterate over a json stream of items and get the field that contains the text to process and tokenize."""
    import json
    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                output = json.loads(line)
                output["filename"] = filename
                yield output
            except ValueError as e:
                logging.warning("Unable to process line: {} (error was: {})".format(str(line), e))


def __is_iterable(obj):
    try:
        iter(obj)
    except TypeError, te:
        return False
    return True


def _iter_large_json(filename, item_prefix='item'):
    """Iterate over all items and sub-items in a json object that match the specified prefix"""
    from ijson import items
    with open(filename, 'r') as f:
        for item in items(f, item_prefix):
            if hasattr(item, 'keys'): # check if item is a dictionary
                yield item
            # check if item is both iterable and not a string
            elif __is_iterable(item) and not isinstance(item, str):
                for sub_item in item:
                    # check if sub_item is a dictionary
                    if hasattr(sub_item, 'keys'):
                        sub_item
            else:
                raise ValueError("'item' in json source is not a dict, and is either a string or not iterable: %r" % item)


def _iter_documents_folder(folder, content_field='text', **kwargs):
    """Iterate over the files in a folder to retrieve the content to process and tokenize."""
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
                logging.warning("Unable to process file: {}, error: {}".format(fullpath, err))


def _iter_solr_query(solr_instance, field, query="*:*", **kwargs):
    import solr
    from topik.utils import batch_concat
    s = solr.SolrConnection(solr_instance)
    response = s.query(query)
    return batch_concat(response, field,  content_in_list=False)


def _iter_elastic_query(instance, index, query=None,
                        year_field=None, id_field=None, **kwargs):
    from elasticsearch import Elasticsearch, helpers
    es = Elasticsearch(instance)

    results = helpers.scan(client=es, index=index, scroll='5m', query=query)

    for result in results:
        yield result['_source']


def read_input(source, content_field, source_type="auto",
               output_type="dictionary", output_args=None,
               synchronous_wait=0, **kwargs):
    """Read data from given source into Topik's internal data structures.

    Parameters
    ----------
    source: (string) input data.  Can be file path, directory, or server address.
    content_field: (string) Which field contains your data to be analyzed.  Hash of this is used as id.
    source_type: (string) "auto" tries to figure out data type of source.  Can be manually specified instead.
        options for manual specification are:
    output_type: (string) internal format for handling user data.  Current options are:
        ["elasticsearch", "dictionary"].  default is "dictionary"
    output_args: (dictionary) configuration to pass through to output
    synchronous_wait: (integer) number of seconds to wait for data to finish uploading to output (this happens
        asynchronously.)  Only relevant for some output types ("elasticsearch", not "dictionary")
    kwargs: any other arguments to pass to input parsers

    Returns
    -------
    iterable output object

    >>> raw_data = read_input(
                '{}/test-data-1.json',
                content_field="text")
    >>> id, text = next(iter(raw_data))
    >>> text
    "'Interstellar' was incredible.  The visuals, the score, the acting,
    were all amazing.  The plot is definitely on of the most original I've
    seen in a while."

    """.format(test_data_path)
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
    if "content_field" not in output_args:
        output_args["content_field"] = content_field
    output = output_formats[output_type](iterable=data_iterator, **output_args)

    if synchronous_wait > 0:
        start = time.time()
        items_stored = output.get_number_of_items_stored()
        time.sleep(1)
        while items_stored != output.get_number_of_items_stored() and time.time() - start < synchronous_wait:
            logging.debug("Number of documents added to the index: {}".format(output.get_number_of_items_stored()))
            time.sleep(1)

    return output
