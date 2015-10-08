import os
import unittest

from topik.readers import read_input
from topik.tokenizers import tokenizer_methods, collect_entities, collect_bigrams_and_trigrams

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)


class TestTokenizers(unittest.TestCase):
    def setUp(self):
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
        _, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["simple"](text, min_length=1)
        self.assertEqual(doc_tokens, self.solution_simple_tokenizer_test_data_json_stream)

    def test_collocations_tokenizer(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        patterns = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=2, min_trigram_freq=2)
        _, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["collocation"](text, patterns=patterns)
        self.assertEqual(doc_tokens, self.solution_collocations_tokenizer_test_data_json_stream)

    def test_entities_tokenizer_json_stream(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        entities = collect_entities(raw_data, freq_min=1)
        _, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["entities"](text, entities)
        self.assertEqual(doc_tokens, self.solution_entities_tokenizer_test_data_json_stream)

    def test_mixed_tokenizer(self):
        raw_data = read_input(
                source=self.data_json_stream_path,
                content_field="abstract",
                output_type="dictionary")
        entities = collect_entities(raw_data)
        id, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["mixed"](text, entities)
        self.assertEqual(doc_tokens, self.solution_mixed_tokenizer_test_data_json_stream)


if __name__ == '__main__':
    unittest.main()
