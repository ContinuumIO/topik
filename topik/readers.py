from __future__ import absolute_import, print_function


import os
import logging

from topik.intermediaries.raw_data import registered_outputs, DictionaryCorpus

# imports used only for doctests
from topik.tests import test_data_path

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def _iter_document_json_stream(filename, json_prefix=None):
    """Iterate over a json stream of items and get the field that contains the text to process and tokenize.

    Parameters
    ----------
    filename : str
        The filename of the json stream.

    Examples
    --------
    >>> documents = _iter_document_json_stream(
    ... '{}/test_data_json_stream.json'.format(test_data_path))
    >>> next(documents) == {
    ... u'doi': u'http://dx.doi.org/10.1557/PROC-879-Z3.3',
    ... u'title': u'Sol Gel Preparation of Ta2O5 Nanorods Using DNA as Structure Directing Agent',
    ... u'url': u'http://journals.cambridge.org/action/displayAbstract?fromPage=online&aid=8081671&fulltextType=RA&fileId=S1946427400119281.html',
    ... u'abstract': u'Transition metal oxides are being considered as the next generation materials in field such as electronics and advanced catalysts; between them is Tantalum (V) Oxide; however, there are few reports for the synthesis of this material at the nanometer size which could have unusual properties. Hence, in this work we present the synthesis of Ta2O5 nanorods by sol gel method using DNA as structure directing agent, the size of the nanorods was of the order of 40 to 100 nm in diameter and several microns in length; this easy method can be useful in the preparation of nanomaterials for electronics, biomedical applications as well as catalysts.',
    ... u'filepath': u'abstracts/879/http%3A%2F%2Fjournals.cambridge.org%2Faction%2FdisplayAbstract%3FfromPage%3Donline%26aid%3D8081671%26fulltextType%3DRA%26fileId%3DS1946427400119281.html',
    ... u'filename': '{}/test_data_json_stream.json'.format(test_data_path),
    ... u'vol': u'879',
    ... u'authors': [u'Humberto A. Monreala', u' Alberto M. Villafa\xf1e',
    ...              u' Jos\xe9 G. Chac\xf3n', u' Perla E. Garc\xeda',
    ...              u'Carlos A. Mart\xednez'],
    ... u'year': u'1917'}
    True

    """
    import json

    with open(filename, 'r') as f:
        for n, line in enumerate(f):
            try:
                output = json.loads(line)
                output["filename"] = filename
                yield output
            except ValueError as e:
                logging.debug("Unable to process line: {} (error was: {})".format(str(line), e))
                raise


def __is_iterable(obj):
    try:
        iter(obj)
    except TypeError as te:
        return False
    return True


def _test_json_input(filename):
    """This is here to test the first item of the JSON stream, so that we raise an exception with
    the _iter_json_stream reader and fall back to _iter_large_json."""
    return next(_iter_document_json_stream(filename))


def _iter_large_json(filename, json_prefix='item'):
    # TODO: add the script to automatically find the json_prefix based on a key
    # Also should still have the option to manually specify a prefix for complex
    # json structures.
    """Iterate over all items and sub-items in a json object that match the specified prefix


    Parameters
    ----------
    filename : str
        The filename of the large json file

    json_prefix : str
        The string representation of the hierarchical prefix where the items of 
        interest may be located within the larger json object.

        Try the following script if you need help determining the desired prefix:
        $   import ijson
        $       with open('test_data_large_json_2.json', 'r') as f:
        $           parser = ijson.parse(f)
        $           for prefix, event, value in parser:
        $               print("prefix = '%r' || event = '%r' || value = '%r'" %
        $                     (prefix, event, value))


    Examples
    --------
    >>> documents = _iter_large_json(
    ...             '{}/test_data_large_json.json'.format(test_data_path),
    ...             json_prefix='item._source.isAuthorOf')
    >>> next(documents) == {
    ... u'a': u'ScholarlyArticle',
    ... u'name': u'Path planning and formation control via potential function for UAV Quadrotor',
    ... u'author': [
    ...     u'http://dig.isi.edu/autonomy/data/author/a.a.a.rizqi',
    ...     u'http://dig.isi.edu/autonomy/data/author/t.b.adji',
    ...     u'http://dig.isi.edu/autonomy/data/author/a.i.cahyadi'],
    ... u'text': u"Potential-function-based control strategy for path planning and formation " +
    ...     u"control of Quadrotors is proposed in this work. The potential function is " +
    ...     u"used to attract the Quadrotor to the goal location as well as avoiding the " +
    ...     u"obstacle. The algorithm to solve the so called local minima problem by utilizing " +
    ...     u"the wall-following behavior is also explained. The resulted path planning via " +
    ...     u"potential function strategy is then used to design formation control algorithm. " +
    ...     u"Using the hybrid virtual leader and behavioral approach schema, the formation " +
    ...     u"control strategy by means of potential function is proposed. The overall strategy " +
    ...     u"has been successfully applied to the Quadrotor's model of Parrot AR Drone 2.0 in " +
    ...     u"Gazebo simulator programmed using Robot Operating System.\\nAuthor(s) Rizqi, A.A.A. " +
    ...     u"Dept. of Electr. Eng. & Inf. Technol., Univ. Gadjah Mada, Yogyakarta, Indonesia " +
    ...     u"Cahyadi, A.I. ; Adji, T.B.\\nReferenced Items are not available for this document.\\n" +
    ...     u"No versions found for this document.\\nStandards Dictionary Terms are available to " +
    ...     u"subscribers only.",
    ... u'uri': u'http://dig.isi.edu/autonomy/data/article/6871517',
    ... u'datePublished': u'2014',
    ... 'filename': '{}/test_data_large_json.json'.format(test_data_path)}
    True
    """

    from ijson import items
    with open(filename, 'r') as f:
        for item in items(f, json_prefix):
            if hasattr(item, 'keys'): # check if item is a dictionary
                item['filename'] = filename
                yield item
            # check if item is both iterable and not a string
            elif __is_iterable(item) and not isinstance(item, str):
                for sub_item in item:
                    # check if sub_item is a dictionary
                    if hasattr(sub_item, 'keys'):
                        sub_item['filename'] = filename
                        yield sub_item
            else:
                raise ValueError("'item' in json source is not a dict, and is either a string or not iterable: %r" % item)


def _iter_documents_folder(folder, content_field='text'):
    """Iterate over the files in a folder to retrieve the content to process and tokenize.

    Parameters
    ----------
    folder : str
        The folder containing the files you want to analyze.

    content_field : str
        The usage of 'content_field' in this source is different from most other sources.  The 
        assumption in this source is that each file contains raw text, NOT dictionaries of 
        categorized data.  The content_field argument here specifies what key to store the raw
        text under in the returned dictionary for each document.

    Examples
    --------
    >>> documents = _iter_documents_folder(
    ...     '{}/test_data_folder_files'.format(test_data_path))
    >>> next(documents)['text'] == (
    ...     u"'Interstellar' was incredible. The visuals, the score, " +
    ...     u"the acting, were all amazing. The plot is definitely one " +
    ...     u"of the most original I've seen in a while.")
    True
    """

    import gzip

    if not os.path.exists(folder):
        raise IOError("Folder not found!")

    for directory, subdirectories, files in os.walk(folder):
        for n, file in enumerate(sorted(files)):
            _open = gzip.open if file.endswith('.gz') else open
            try:
                fullpath = os.path.join(directory, file)
                with _open(fullpath, 'rb') as f:
                    yield {content_field: f.read().decode('utf-8'),
                           'filename': fullpath}
            except (ValueError, UnicodeDecodeError) as err:
                logging.warning("Unable to process file: {}, error: {}".format(fullpath, err))


def _iter_solr_query(solr_instance, content_field, query="*:*", content_in_list=True, **kwargs):
    # TODO: should I be checking for presence of content_field and year_field?
    # If not then we don't need them as params
    # TODO: should I care at this level whether the content_in_list or only at
    # the read_input level?  Is it being handled at that level currently?
    """Iterate over all documents in the specified solr intance that match the specified query

    Parameters
    ----------
    solr_instance : str
        Address of the solr instance
    content_field : str
        The name fo the field that contains the main text body of the document.
    query : str
        The solr query string
    content_in_list: bool
        Whether the source fields are stored in single-element lists.  Used for unpacking.
    """

    import pysolr

    s = pysolr.Solr(solr_instance)
    results_per_batch = 100
    response = s.select(query, rows=results_per_batch)
    while response.results:
        for item in response.results:
            if content_in_list:
                if content_field in item.keys() and type(item[content_field]) == list:
                    item[content_field] = item[content_field][0]
            yield item
        response = response.next_batch()


def _iter_elastic_query(hosts, **kwargs):
    """Iterate over all documents in the specified elasticsearch intance and index that match the specified query.

    kwargs are passed to Elasticsearch class instantiation, and can be used to pass any additional options
    described at https://elasticsearch-py.readthedocs.org/en/master/

    Parameters
    ----------
    hosts : str or list
        Address of the elasticsearch instance any index.  May include port, username and password.
        See https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch for all options.

    content_field : str
        The name fo the field that contains the main text body of the document.

    **kwargs: additional keyword arguments to be passed to Elasticsearch client instance and to scan query.
              See
              https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch for all client options.
              https://elasticsearch-py.readthedocs.org/en/master/helpers.html#elasticsearch.helpers.scan for all scan options.
    """

    from elasticsearch import Elasticsearch, helpers
    es = Elasticsearch(hosts, **kwargs)
    results = helpers.scan(es, **kwargs)
    for result in results:
        yield result['_source']


def read_input(source, content_field, source_type="auto",
               output_type=DictionaryCorpus.class_key(), output_args=None,
               synchronous_wait=0, **kwargs):
    """
    Read data from given source into Topik's internal data structures.

    Parameters
    ----------
    source : str
        input data.  Can be file path, directory, or server address.
    content_field : str
        Which field contains your data to be analyzed.  Hash of this is used as id.
    source_type : str
        "auto" tries to figure out data type of source.  Can be manually specified instead.
        options for manual specification are ['solr', 'elastic', 'json_stream', 'large_json', 'folder']
    output_type : str
        Internal format for handling user data.  Current options are in the registered_outputs dictionary.
        Default is DictionaryCorpus class.  Specify alternatives using string key from dictionary.
    output_args : dict
        Configuration to pass through to output
    synchronous_wait : positive, real number
        Time in seconds to wait for data to finish uploading to output (this happens
        asynchronously.)  Only relevant for some output types ("elastic", not "dictionary")
    kwargs : any other arguments to pass to input parsers

    Returns
    -------
    iterable output object


    Examples
    --------
    >>> raw_data = read_input(
    ...         '{}/test_data_json_stream.json'.format(test_data_path),
    ...          content_field="abstract")
    >>> id, text = next(iter(raw_data))
    >>> text == (
    ... u'Transition metal oxides are being considered as the next generation '+
    ... u'materials in field such as electronics and advanced catalysts; '+
    ... u'between them is Tantalum (V) Oxide; however, there are few reports '+
    ... u'for the synthesis of this material at the nanometer size which could '+
    ... u'have unusual properties. Hence, in this work we present the '+
    ... u'synthesis of Ta2O5 nanorods by sol gel method using DNA as structure '+
    ... u'directing agent, the size of the nanorods was of the order of 40 to '+
    ... u'100 nm in diameter and several microns in length; this easy method '+
    ... u'can be useful in the preparation of nanomaterials for electronics, '+
    ... u'biomedical applications as well as catalysts.')
    True
    """

    import time
    json_extensions = [".js", ".json"]
    if output_args is None:
        output_args = {}

    # solr defaults to port 8983
    if (source_type == "auto" and "8983" in source) or source_type == "solr":
        data_iterator = _iter_solr_query(source, **kwargs)
    # web addresses default to elasticsearch
    elif (source_type == "auto" and "9200" in source) or source_type == "elastic":
        data_iterator = _iter_elastic_query(source, **kwargs)
    # files must end in .json.  Try json parser first, try large_json parser next.  Fail otherwise.
    elif (source_type == "auto" and os.path.splitext(source)[1] in json_extensions) or source_type == "json_stream":
        try:
            _test_json_input(source)
            data_iterator = _iter_document_json_stream(source, **kwargs)
        except ValueError as e:
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
    output = registered_outputs[output_type](iterable=data_iterator, **output_args)

    if synchronous_wait > 0:
        start = time.time()
        items_stored = len(output)
        time.sleep(1)
        # TODO: might get into trouble here if upload is actually empty!
        while len(output) <= 0 or (items_stored != len(output) and time.time() - start < synchronous_wait):
            logging.debug("Number of documents added to the index: {}".format(len(output)))
            time.sleep(1)
            items_stored = len(output)
        if time.time() - start > synchronous_wait:
            logging.warning("Number of documents had not stabilized by end of synchronous_wait, continuing anyway.")
    return output
