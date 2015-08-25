import os
import unittest

from topik.readers import _iter_document_json_stream, _iter_documents_folder

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)


class TestReader(unittest.TestCase):

    def setUp(self):
        self.solution = str("'Interstellar' was incredible. The visuals, the score, the acting, were all amazing."
                            " The plot is definitely one of the most original I've seen in a while.")

    def test_iter_document_json_stream(self):
        iterable_data = _iter_document_json_stream(
                os.path.join(module_path, 'data/test-data-1.json'))
        first_text = next(iterable_data)
        self.assertEqual(first_text["text"], self.solution)

    def test_iter_document_json_stream_with_year_field(self):
        raise NotImplementedError, "TODO: need data source that actually has date data!  test-data-1.json does not!"
        iterable_data = _iter_document_json_stream(
                os.path.join(module_path, 'data/test-data-1.json'))
        first_text = next(iterable_data)
        self.assertEqual(first_text, self.solution)

    def test_iter_documents_folder(self):
        loaded_dictionaries = _iter_documents_folder(
                os.path.join(module_path, 'data/test-data-folder'))
        for entry in loaded_dictionaries:
            if "doc1" in entry["filename"]:
                self.assertEqual(entry["text"], self.solution)
                break

    def test_iter_documents_folder_gz(self):
        loaded_dictionaries = _iter_documents_folder(
                os.path.join(module_path, 'data/test-data-folder-gz'))
        for entry in loaded_dictionaries:
            if "doc1.gz" in entry["filename"]:
                self.assertEqual(entry["text"], self.solution)
                break

if __name__ == '__main__':
    unittest.main()
