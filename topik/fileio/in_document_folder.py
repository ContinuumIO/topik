import os
import logging
import gzip

from topik.fileio._registry import register_input
from topik.fileio.tests import test_data_path

@register_input
def read_document_folder(folder, content_field='text'):
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
    >>> documents = read_document_folder(
    ...     '{}/test_data_folder_files'.format(test_data_path))
    >>> next(documents)['text'] == (
    ...     u"'Interstellar' was incredible. The visuals, the score, " +
    ...     u"the acting, were all amazing. The plot is definitely one " +
    ...     u"of the most original I've seen in a while.")
    True
    """

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
