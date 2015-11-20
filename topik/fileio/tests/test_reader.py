import nose.tools as nt

from topik.fileio.reader import read_input
from topik.fileio.tests import test_data_path
from ._solutions import solution_json_stream, solution_large_json,\
                        solution_document_folder, solution_document_folder_gz

def test_read_input():
    # json stream
    documents = read_input('{}/test_data_json_stream.json'.format(test_data_path))
    nt.assert_true(next(documents)['abstract'] == solution_json_stream)

    # large json
    documents = read_input('{}/test_data_large_json.json'.format(test_data_path),
                               json_prefix='item._source.isAuthorOf')
    nt.assert_true(next(documents)['text'] == solution_large_json)

    # document folder
    documents = read_input(
        '{}/test_data_folder_files'.format(test_data_path),
        folder_content_field="abstract")
    nt.assert_true(next(documents)['abstract'] == solution_document_folder)

    # document folder gz
    documents = read_input(
        '{}/test_data_folder_files_gz'.format(test_data_path),
        folder_content_field="abstract")
    nt.assert_true(next(documents)['abstract'] == solution_document_folder_gz)

    # TODO: add elastic and solr
