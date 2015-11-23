import logging

import json
import ijson

from topik.fileio._registry import register_input
from topik.fileio.tests import test_data_path

@register_input
def read_json_stream(filename, json_prefix='item', **kwargs):
    # TODO: decide between:
    #   a) allow this unused json_prefix argument so that current check in read_input works
    #   b) allow **kwargs instead
    #   c) improve the check in read_input.. (maybe read first line and see if it is a valid, self-contained json object?
    #   d) actually do use an optional json_prefix argument to only return a subset of each json object.

    """Iterate over a json stream of items and get the field that contains the text to process and tokenize.

    Parameters
    ----------
    filename : str
        The filename of the json stream.

    Examples
    --------
    >>> documents = read_json_stream(
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


@register_input
def read_large_json(filename, json_prefix='item', **kwargs):
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
    >>> documents = read_large_json(
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

    with open(filename, 'r') as handle:
        for item in ijson.items(handle, json_prefix):
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

