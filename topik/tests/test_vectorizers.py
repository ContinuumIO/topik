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

        self.dictionary_values_simple_test_data_json_stream = [
            u'transition', u'metal', u'oxides', u'considered',
            u'generation', u'materials', u'field', u'electronics',
            u'advanced', u'catalysts', u'tantalum', u'v', u'oxide',
            u'reports', u'synthesis', u'material', u'nanometer', u'size',
            u'unusual', u'properties', u'work', u'present', u'synthesis',
            u'ta', u'o', u'nanorods', u'sol', u'gel', u'method', u'dna',
            u'structure', u'directing', u'agent', u'size', u'nanorods',
            u'order', u'nm', u'diameter', u'microns', u'length', u'easy',
            u'method', u'useful', u'preparation', u'nanomaterials', u'electronics',
            u'biomedical', u'applications', u'catalysts']


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
        self.tokenized_data = raw_data.tokenize(min_length=1)

    def test_corpus_bow_content(self):
        for i, term in enumerate(self.dictionary_values_simple_test_data_json_stream):
            #print(i)
            #print(term)
            #print(list(iter(self.tokenized_data))[i])
            #print(list(self.tokenized_data._corpus)[i])
            #print(self.corpus_bow_head_2_simple_test_data_json_stream[i])
            self.assertTrue(term in self.tokenized_data._dict.values())

    def test_corpus_word_counts(self):
        # Since the order in which the documents are processed into the dictionary
        # cannot be guaranteed, the term ids also cannot be guaranteed.  As a
        # result, we simply look for a document whose text tokens match the
        # solution token set above, and then confirm that their corresponding
        # BOW representations match in terms of 1) count of unique terms, and 2)
        # count of total terms.  Once we implement storage of terms with term ids
        # in a more complete Dictionary object, we may be able to improve this
        # test.
        found = False
        for i, tokenized_doc in enumerate(list(self.tokenized_data._corpus)):
            if self.dictionary_values_simple_test_data_json_stream == \
                tokenized_doc[1]:
                found = True
                self.assertEqual(len(self.corpus_bow_head_2_simple_test_data_json_stream),
                                 len(list(iter(self.tokenized_data))[i]))
                solution_ids, solution_counts = \
                    zip(*self.corpus_bow_head_2_simple_test_data_json_stream)
                found_ids, found_counts = zip(*list(iter(self.tokenized_data))[i])
                self.assertEqual(sum(solution_counts), sum(found_counts))
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
