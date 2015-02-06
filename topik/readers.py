from __future__ import absolute_import

import json
import os
import logging
import codecs

from topik.utils import head

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def iter_document_json_stream(filename, field):
    """
    Iterate over a json stream of items and get the field that contains the text to process and tokenize.

    Parameters
    ----------
    filename: string
        The filename of the json stream.

    field: string
        The field name that contains the text that needs to be processed

    $ head -n 2 ./topik/tests/data/test-data-1
        {"id": 1, "topic": "interstellar film review", "text":"'Interstellar' was incredible. The visuals, the score..."}
        {"id": 2, "topic": "big data", "text": "Big Data are becoming a new technology focus both in science and in..."}
    >>> doc_text = iter_document_json_stream('./topik/tests/data/test-data-1', "text")
    >>> head(doc_text)
    [u"'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one
    of the most original I've seen in a while."]
    """

    with open(filename, 'r') as f:
        for line in f.readlines():
            try:
                dictionary = json.loads(line)
                content = dictionary.get(field)
                yield content
            except ValueError:
                logging.warning("Unable to process line:\n\t%s" %str(line))



def iter_documents_folder(folder):
    """
    Iterate over the files in a folder to retrieve the content to process and tokenize.

    Parameters
    ----------
    folder: string
        The folder containing the files you want to analyze.

    $ ls ./topik/tests/test-data-folder
        doc1  doc2  doc3
    >>> doc_text = iter_documents_folder('./topik/tests/test-data-1')
    >>> head(doc_text)
    [u"'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one
    of the most original I've seen in a while."]
    """

    for directory, subdirectories, files in os.walk(folder):
        for file in files:
            try:
                with codecs.open(os.path.join(directory, file), "r", "utf-8") as f:
                    content = f.read()
                    yield content
            except ValueError:
                logging.warning("Unable to process file:\n\t %s" %str(file))


def iter_large_json(json_file, prefix_value, event_value):
    import ijson

    parser = ijson.parse(open(json_file))

    for prefix, event, value in parser:
        # For Flowdock data ('item.content', 'string')
        if (prefix, event) == (prefix_value, event_value):
            yield value

