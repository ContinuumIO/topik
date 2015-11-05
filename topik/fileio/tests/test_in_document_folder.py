import nose.tools as nt

from topik.fileio import document_folder
from topik.tests import test_data_path
from ._solutions import solution_document_folder, solution_document_folder_gz

def test_read_document_folder():
    loaded_corpus = document_folder(
        '{}/test_data_folder_files'.format(test_data_path),
        content_field="abstract")
    nt.assert_true(solution_document_folder == next(iter(loaded_corpus))['abstract'])

def test_read_document_folder_gz():
    loaded_corpus = document_folder(
        '{}/test_data_folder_files_gz'.format(test_data_path),
        content_field="abstract")
    nt.assert_true(solution_document_folder_gz == next(iter(loaded_corpus))['abstract'])
