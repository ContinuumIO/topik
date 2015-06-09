import unittest

from topik.readers import iter_document_json_stream, iter_documents_folder
from topik.utils import unzip

class TestReader(unittest.TestCase):

    def setUp(self):
        self.solution = "'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. \
                                        The plot is definitely one of the most original I've seen in a while."

    def test_iter_document_json_stream(self):
        id_documents = iter_document_json_stream(
                './topik/tests/data/test-data-1.json', "text")
        ids, doc_text = unzip(id_docuents)
        first_document = next(doc_text)
        self.assertTrue(first_document, self.solution)

    def test_iter_documents_folder(self):
        id_documents = iter_documents_folder(
                './topik/tests/data/test-data-folder')
        ids, doc_text = unzip(id_documents)
        for fname, document in doc_text:
            if fname=='doc1':
                self.assertTrue(document, self.solution)
                break

    def test_iter_documents_folder_gz(self):
        id_documents = iter_documents_folder(
                './topik/tests/data/test-data-folder-gz')
        ids, doc_text = unzip(id_documents)
        for fname, document in doc_text:
            if fname=='doc1.gz':
                self.assertTrue(document, self.solution)
                break

if __name__ == '__main__':
    unittest.main()
