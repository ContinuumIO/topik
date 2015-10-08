import os
import unittest

from topik.readers import read_input
from topik.tests import test_data_path


class TestCorpusBOW(unittest.TestCase):
    def setUp(self):
        self.dictionary_values_simple_test_data_1 = [
                'bending', 'sci', 'forget', 'messi', 'skip',
                'hands', 'focus', 'comply', 'colors', 'planning']

        self.dictionary_values_simple_test_data_json_stream = [
            u'limited', u'consolidated', u'magnetic', u'comparatively',
            u'powders', u'waspaloy', u'tensile', u'assembled', u'relationships',
            u'sfft']

        self.corpus_bow_head_2_simple_test_data_1 = [
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (6, 1), (7, 1), (8, 1), (9, 1), (10, 1)]

        self.corpus_bow_head_2_simple_test_data_json_stream = [
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
            (8, 1), (9, 2), (10, 1), (11, 1), (12, 1), (13, 1), (14, 2),
            (15, 2), (16, 1), (17, 1), (18,1), (19, 2), (20, 2), (21, 2),
                (22, 1), (23, 1), (24, 1), (25, 1), (26, 1), (27, 1), (28, 1),
                (29, 1), (30, 1), (31, 1), (32, 1), (33, 1), (34, 1), (35, 1),
                (36, 1), (37, 1), (38, 1), (39, 1), (40, 1), (41, 1), (42, 1)]

        raw_data = read_input(os.path.join(test_data_path,
                                           'test_data_json_stream.json'),
                                   content_field="abstract",
                                   output_type="dictionary")
        self.processed_data = raw_data.tokenize(min_length=1)

    def test_corpus_bow_content(self):
        self.assertEqual(self.processed_data._dict.values()[:10],
                        self.dictionary_values_simple_test_data_json_stream)

    def test_corpus_word_counts(self):
        self.assertEqual(next(iter(self.processed_data)),
                         self.corpus_bow_head_2_simple_test_data_json_stream)

if __name__ == '__main__':
    unittest.main()
