import os
import unittest

from topik.readers import read_input
from topik.intermediaries.raw_data import ElasticSearchCorpus, _get_hash_identifier
from topik.tokenizers import tokenizer_methods, find_entities, collect_trigrams_and_bigrams

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)

class TestTokenizers(unittest.TestCase):
    def setUp(self):
        self.solution_simple_tokenizer_test_data_1 = [
            'interstellar', 'incredible', 'visuals', 'score', 'acting',
            'amazing', 'plot', 'definitely', 'original', 've', 'seen']

        self.solution_collocations_tokenizer_test_data_2 = [
            'paper', 'simple', 'rapid', 'solution', 'phase', 'chemical',
            'reduction', 'method', 'inert', 'gas', 'protection',
            'preparing', 'stable', 'copper', 'nanoparticle', 'colloid',
            'average', 'particle', 'size', 'narrow', 'size_distribution',
            'synthesis_route', 'ascorbic_acid', 'natural', 'vitamin',
            'serves', 'reducing', 'agent', 'antioxidant', 'reduce',
            'copper', 'salt', 'precursor', 'effectively', 'prevent',
            'general', 'oxidation', 'process', 'occurring', 'newborn',
            'nanoparticles', 'xrd', 'vis', 'confirm', 'formation', 'pure',
            'face', 'centered', 'cubic', 'fcc', 'copper', 'nanoparticles',
            'excellent', 'antioxidant', 'ability', 'ascorbic_acid']

        self.solution_entities_tokenizer_test_data_2 = [
            'rapid_solution_phase_chemical_reduction_method',
            'inert_gas_protection', 'stable_copper_nanoparticle_colloid',
            'average_particle_size', 'narrow_size_distribution',
            'synthesis_route', 'ascorbic_acid', 'natural_vitamin_c', 'vc',
            'copper_salt_precursor', 'general_oxidation_process',
            'newborn_nanoparticles', 'xrd', 'uv_vis',
            'copper_nanoparticles', 'excellent_antioxidant_ability',
            'ascorbic_acid']

        self.solution_mixed_tokenizer_test_data_2 = [
            'rapid', 'solution', 'phase', 'chemical', 'reduction',
            'method', 'inert', 'gas', 'protection', 'stable', 'copper',
            'nanoparticle', 'colloid', 'average', 'particle', 'size',
            'narrow', 'size', 'distribution', 'synthesis_route',
            'ascorbic_acid', 'natural', 'vitamin', 'c', 'copper', 'salt',
            'precursor', 'general', 'oxidation', 'process', 'newborn',
            'nanoparticles', 'xrd', 'vis', 'copper', 'nanoparticles',
            'excellent', 'antioxidant', 'ability', 'ascorbic_acid']

        self.data_1_path = os.path.join(module_path, 'data/test-data-1.json')
        self.data_2_path = os.path.join(module_path, 'data/test-data-2.json')
        assert os.path.exists(self.data_1_path)
        assert os.path.exists(self.data_2_path)

    def test_simple_tokenizer(self):
        raw_data = read_input(
                source=self.data_1_path,
                content_field="text",
                output_type="dictionary")
        id, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["simple"](text)
        self.assertEqual(doc_tokens,
                         self.solution_simple_tokenizer_test_data_1)

    def test_collocations_tokenizer(self):
        raw_data = read_input(
                source=self.data_2_path,
                content_field="abstract",
                output_type="dictionary")
        bigrams, trigrams = collect_trigrams_and_bigrams(raw_data, min_bigram_freq=2, min_trigram_freq=2)
        id, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["collocation"](text, bigrams, trigrams)
        self.assertEqual(doc_tokens,
                         self.solution_collocations_tokenizer_test_data_2)

    def test_entities_tokenizer(self):
        raw_data = read_input(
                source=self.data_2_path,
                content_field="abstract",
                output_type="dictionary")
        entities = find_entities(raw_data, freq_min=1)
        id, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["entities"](text, entities)
        self.assertEqual(doc_tokens,
                         self.solution_entities_tokenizer_test_data_2)

    def test_mixed_tokenizer(self):
        raw_data = read_input(
                source=self.data_2_path,
                content_field="abstract",
                output_type="dictionary")
        entities = find_entities(raw_data, freq_min=1)
        id, text = next(iter(raw_data))
        doc_tokens = tokenizer_methods["mixed"](text, entities)
        self.assertEqual(doc_tokens,
                         self.solution_mixed_tokenizer_test_data_2)


if __name__ == '__main__':
    unittest.main()
