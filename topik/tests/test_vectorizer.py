import os
import unittest

from topik.readers import _iter_document_json_stream
from topik.tokenizers import SimpleTokenizer
from topik.vectorizers import CorpusBOW

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)


class TestCorpusBOW(unittest.TestCase):
    def setUp(self):
        self.dictionary_values_simple_test_data_1 = [
                'bending', 'sci', 'forget', 'messi', 'skip',
                'hands', 'focus', 'comply', 'colors', 'planning']

        self.corpus_bow_head_2_simple_test_data_1 = [
                [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
                 (7, 1), (8, 1), (9, 1), (10, 1)],
                [(11, 1), (12, 1), (13, 1), (14, 2),
                 (15, 1), (16, 1),(17, 1), (18, 1), (19, 1), (20, 1),
                 (21, 1), (22, 1), (23, 2)]]

        fullpath = os.path.join(module_path, 'data/test-data-1.json')
        id_documents = iter_document_json_stream(fullpath, "text")
        self.my_corpus = SimpleTokenizer(texts)

    def test_corpus_bow_content(self):
        corpus_bow = CorpusBOW(self.my_corpus)
        self.assertTrue(next(corpus_bow.dict.values()),
                        self.dictionary_values_simple_test_data_1)

    def test_corpus_bow_save_dict(self):
        corpus_bow = CorpusBOW(self.my_corpus)
        dict_fname = 'test-data-1.dict'
        corpus_bow.save_dict(os.path.join(module_path, dict_fname))

        self.assertTrue(os.path.isfile(os.path.join(module_path, dict_fname)))

    def test_corpus_bow_serialize(self):
        corpus_bow = CorpusBOW(self.my_corpus)
        corpus_fname = 'test-data-1.mm'
        corpus_bow.serialize(os.path.join(module_path, corpus_fname))
        self.assertTrue(os.path.isfile(os.path.join(module_path, corpus_fname)))


if __name__ == '__main__':
    unittest.main()
