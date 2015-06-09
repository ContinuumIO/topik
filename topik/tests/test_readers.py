import unittest

from topik.readers import iter_document_json_stream, iter_documents_folder
from topik.utils import unzip

class TestReader(unittest.TestCase):

    def setUp(self):
        self.solution = "'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. \
                                        The plot is definitely one of the most original I've seen in a while."

    def test_iter_document_json_stream(self):
        id_texts = iter_document_json_stream(
                './topik/tests/data/test-data-1.json', "text")
        ids, texts = unzip(id_texts)
        first_text = next(texts)
        self.assertTrue(first_text, self.solution)

    def test_iter_documents_folder(self):
        id_texts = iter_documents_folder(
                './topik/tests/data/test-data-folder')
        for fname, text in id_texts:
            if fname=='doc1':
                self.assertTrue(text, self.solution)
                break

    def test_iter_documents_folder_gz(self):
        id_texts = iter_documents_folder(
                './topik/tests/data/test-data-folder-gz')
        for fname, text in id_texts:
            if fname=='doc1.gz':
                self.assertTrue(text, self.solution)
                break

if __name__ == '__main__':
    unittest.main()
