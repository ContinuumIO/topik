import os
import unittest

from topik.readers import read_input
from topik.preprocessing import preprocess

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

        raw_data = read_input(os.path.join(module_path, 'data/test-data-1.json'),
                                   content_field="text",
                                   output_type="dictionary")
        self.processed_data = preprocess(raw_data)

    def test_corpus_bow_content(self):
        self.assertTrue(next(self.processed_data.dict.values()),
                        self.dictionary_values_simple_test_data_1)

    def test_corpus_word_counts(self):
        raise NotImplementedError("This is probably what that data set of tuples is for...")

if __name__ == '__main__':
    unittest.main()
