import os
import unittest

from topik.readers import read_input
from topik.intermediaries.raw_data import ElasticSearchCorpus, _get_hash_identifier
from topik.tokenizers import tokenizer_methods

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

        self.output_config = {"host": "localhost",
                         "index": "tokenizer_testing",
                         "text_field": "text"}
        es = ElasticSearchCorpus(**self.output_config)
        if es.instance.indices.exists("tokenizer_testing"):
            es.instance.indices.delete("tokenizer_testing")
        self.raw_data = None

        self.data_1_path = os.path.join(module_path, 'data/test-data-1.json')
        self.data_2_path = os.path.join(module_path, 'data/test-data-2')
        assert os.path.exists(self.data_1_path)
        assert os.path.exists(self.data_2_path)

    def tearDown(self):
        es = ElasticSearchCorpus(**self.output_config)
        es.instance.indices.delete("tokenizer_testing")

    def test_simple_tokenizer(self):
        raw_data = read_input(
                source=self.data_1_path,
                content_field=self.output_config["text_field"],
                output_args=self.output_config,
                synchronous_wait=10)
        raw_data = raw_data.instance.search(index="tokenizer_testing", _source="text",
                                            body={"query": {"match": {'id': "1"}}})['hits']['hits'][0]["_source"]["text"]
        doc_tokens = tokenizer_methods["simple"](raw_data)
        self.assertEqual(doc_tokens,
                         self.solution_simple_tokenizer_test_data_1)

    def test_collocations_tokenizer(self):
        raw_data = read_input(
                source=self.data_2_path,
                content_field=self.output_config["text_field"],
                output_args=self.output_config)
        collocations_tokenizer = CollocationsTokenizer(raw_data,
                                  min_bigram_freq=2, min_trigram_freq=2)
        doc_tokens = next(iter(collocations_tokenizer))
        self.assertEqual(doc_tokens,
                         self.solution_collocations_tokenizer_test_data_2)

    def test_entities_tokenizer(self):
        raw_data = read_input(
                source=self.data_2_path,
                content_field=self.output_config["text_field"],
                output_args=self.output_config)
        entities_tokenizer = EntitiesTokenizer(raw_data, 1)
        doc_tokens = next(iter(entities_tokenizer))
        self.assertEqual(doc_tokens,
                         self.solution_entities_tokenizer_test_data_2)

    def test_mixed_tokenizer(self):
        raw_data = read_input(
                source=self.data_2_path,
                content_field=self.output_config["text_field"],
                output_args=self.output_config)
        mixed_tokenizer = MixedTokenizer(raw_data)
        doc_tokens = next(iter(mixed_tokenizer))
        self.assertEqual(doc_tokens,
                         self.solution_mixed_tokenizer_test_data_2)


if __name__ == '__main__':
    unittest.main()
