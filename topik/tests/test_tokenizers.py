import os
import unittest

from topik.readers import read_input
from topik.tokenizers import tokenizer_methods, collect_entities, collect_bigrams_and_trigrams

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)


class TestTokenizers(unittest.TestCase):
    def setUp(self):
        self.raw_text = 'Transition metal oxides are being considered as the next generation materials in field such as electronics and advanced catalysts; between them is Tantalum (V) Oxide; however, there are few reports for the synthesis of this material at the nanometer size which could have unusual properties. Hence, in this work we present the synthesis of Ta2O5 nanorods by sol gel method using DNA as structure directing agent, the size of the nanorods was of the order of 40 to 100 nm in diameter and several microns in length; this easy method can be useful in the preparation of nanomaterials for electronics, biomedical applications as well as catalysts.'
        self.raw_text2 = str(
            'Transition metal oxides are being considered as the next '
            'generation materials in field such as electronics and advanced '
            'catalysts; between them is Tantalum (V) Oxide; however, there are '
            'few reports for the synthesis of this material at the nanometer '
            'size which could have unusual properties. Hence, in this work we '
            'present the synthesis of Ta2O5 nanorods by sol gel method using '
            'DNA as structure directing agent, the size of the nanorods was of '
            'the order of 40 to 100 nm in diameter and several microns in '
            'length; this easy method can be useful in the preparation of '
            'nanomaterials for electronics, biomedical applications as well as '
            'catalysts.')

        self.solution_simple_tokenizer_test_data_json_stream = [
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

        self.solution_collocations_tokenizer_test_data_json_stream = [
            u'transition_metal', u'oxides', u'considered', u'generation',
            u'materials', u'field', u'electronics', u'advanced', u'catalysts',
            u'tantalum', u'v_oxide', u'reports', u'synthesis_material',
            u'nanometer_size', u'unusual', u'properties', u'work_present',
            u'synthesis', u'ta', u'o', u'nanorods', u'sol', u'gel', u'method',
            u'dna', u'structure', u'directing', u'agent', u'size', u'nanorods',
            u'order', u'nm_diameter', u'microns', u'length', u'easy', u'method',
            u'useful', u'preparation', u'nanomaterials', u'electronics', u'biomedical',
            u'applications', u'catalysts']

        self.solution_entities_tokenizer_test_data_json_stream = [
            u'transition', u'metal_oxides', u'generation_materials',
            u'tantalum', u'oxide', u'nanometer_size', u'unusual_properties',
            u'ta_o', u'sol_gel_method', u'dna', u'easy_method',
            u'biomedical_applications']

        self.solution_mixed_tokenizer_test_data_json_stream = [
            u'transition', u'metal', u'oxides', u'generation', u'materials',
            u'tantalum', u'oxide', u'nanometer', u'size', u'unusual', u'properties',
            u'ta_o', u'sol', u'gel', u'method', u'dna', u'easy', u'method',
            u'biomedical', u'applications']

        self.data_json_stream_path = os.path.join(module_path, 'data/test_data_json_stream.json')
        self.data_large_json_path = os.path.join(module_path, 'data/test_data_large_json.json')
        assert os.path.exists(self.data_json_stream_path)
        assert os.path.exists(self.data_large_json_path)

    def test_simple_tokenizer(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        tokenized_data = raw_data.tokenize()
        ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
        self.assertTrue(self.solution_simple_tokenizer_test_data_json_stream in\
                        tokenized_texts)

    def test_collocations_tokenizer(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        patterns = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=2,
                                                min_trigram_freq=2)
        tokenized_data = raw_data.tokenize(method="collocation",
                                           patterns=patterns)
        ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
        self.assertTrue(self.solution_collocations_tokenizer_test_data_json_stream in\
                        tokenized_texts)

    def test_entities_tokenizer_json_stream(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        entities = collect_entities(raw_data, freq_min=1)
        tokenized_data = raw_data.tokenize(method="entities",
                                           entities=entities)
        ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
        self.assertTrue(self.solution_entities_tokenizer_test_data_json_stream in\
                        tokenized_texts)

    def test_mixed_tokenizer(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        entities = collect_entities(raw_data)
        tokenized_data = raw_data.tokenize(method="mixed",
                                           entities=entities)
        ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
        self.assertTrue(self.solution_mixed_tokenizer_test_data_json_stream in\
                        tokenized_texts)


if __name__ == '__main__':
    unittest.main()
