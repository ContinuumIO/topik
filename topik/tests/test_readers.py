import unittest

from topik.readers import iter_document_json_stream, iter_documents_folder, head



class TestReader(unittest.TestCase):

    def setUp(self):
        self.solution_first_document = "'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. \
                                        The plot is definitely one of the most original I've seen in a while."

    def test_iter_document_json_stream(self):
        doc_text = iter_document_json_stream('./topik/tests/data/test-data-1', "text")
        first_document = head(doc_text)
        self.assertTrue(first_document, self.solution_first_document)

    def test_iter_documents_folder(self):
        doc_text = iter_documents_folder('./topik/tests/data/test-data-folder')
        first_document = head(doc_text)
        self.assertTrue(first_document, self.solution_first_document)


if __name__ == '__main__':
    unittest.main()