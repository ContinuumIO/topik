import nose.tools as nt

from topik.fileio import read_document_folder
from topik.fileio.tests import test_data_path
from ._solutions import solution_document_folder, solution_document_folder_gz


def test_read_document_folder():
    documents = read_document_folder(
        '{}/test_data_folder_files'.format(test_data_path),
        content_field="abstract")
    nt.assert_true(solution_document_folder == next(iter(documents))['abstract'])


def test_read_document_folder_junk():
    documents = read_document_folder(
        '{}/test_data_folder_files_junk'.format(test_data_path),
        content_field="abstract")
    nt.assert_true(solution_document_folder == next(iter(documents))['abstract'])


def test_read_document_folder_gz():
    documents = read_document_folder(
        '{}/test_data_folder_files_gz'.format(test_data_path),
        content_field="abstract")
    nt.assert_true(solution_document_folder_gz == next(iter(documents))['abstract'])


def test_bad_folder():
    nt.assert_raises(IOError, next, read_document_folder("Frank",
                                                         content_field='theTank'))