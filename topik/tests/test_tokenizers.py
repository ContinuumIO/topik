import unittest

from topik.readers import iter_document_json_stream
from topik.tokenizers import (SimpleTokenizer, CollocationsTokenizer, 
                              EntitiesTokenizer, MixedTokenizer

class TestTokenizers(unittest.TestCase):
    def setUp(self):
	self.solution_simple_tokenizer_test_data_1 = [
	    ['interstellar', 'incredible', 'visuals', 'score', 'acting',
	     'amazing', 'plot', 'definitely', 'original', 've', 'seen']]

	self.solution_collocations_tokenizer_test_data_2 = [
	    ['paper', 'simple', 'rapid', 'solution', 'phase', 'chemical',
	     'reduction', 'method', 'inert', 'gas', 'protection',
	     'preparing', 'stable', 'copper', 'nanoparticle', 'colloid',
	     'average', 'particle', 'size', 'narrow', 'size_distribution',
	     'synthesis_route', 'ascorbic_acid', 'natural', 'vitamin',
	     'serves', 'reducing', 'agent', 'antioxidant', 'reduce',
	     'copper', 'salt', 'precursor', 'effectively', 'prevent',
	     'general', 'oxidation', 'process', 'occurring', 'newborn',
	     'nanoparticles', 'xrd', 'vis', 'confirm', 'formation', 'pure',
	     'face', 'centered', 'cubic', 'fcc', 'copper', 'nanoparticles',
	     'excellent', 'antioxidant', 'ability', 'ascorbic_acid']]

	self.solution_entities_tokenizer_test_data_2 = [
	    ['rapid_solution_phase_chemical_reduction_method',
	     'inert_gas_protection', 'stable_copper_nanoparticle_colloid',
	     'average_particle_size', 'narrow_size_distribution',
	     'synthesis_route', 'ascorbic_acid', 'natural_vitamin_c', 'vc',
	     'copper_salt_precursor', 'general_oxidation_process',
	     'newborn_nanoparticles', 'xrd', 'uv_vis',
	     'copper_nanoparticles', 'excellent_antioxidant_ability',
	     'ascorbic_acid']]

        self.solution_mixed_tokenizer_test_data_2 = [
	    ['rapid', 'solution', 'phase', 'chemical', 'reduction',
	     'method', 'inert', 'gas', 'protection', 'stable', 'copper',
	     'nanoparticle', 'colloid', 'average', 'particle', 'size',
	     'narrow', 'size', 'distribution', 'synthesis_route',
	     'ascorbic_acid', 'natural', 'vitamin', 'c', 'copper', 'salt',
	     'precursor', 'general', 'oxidation', 'process', 'newborn',
	     'nanoparticles', 'xrd', 'vis', 'copper', 'nanoparticles',
	     'excellent', 'antioxidant', 'ability', 'ascorbic_acid']]

    def test_simple_tokenizer(self):
        id_documents = iter_document_json_stream(
            './topik/tests/data/test-data-1', "text")
        ids, doc_text = unzip(id_documents)
        simple_tokenizer = SimpleTokenizer(doc_text)
        doc_tokens = next(iter(simple_tokenizer))
        self.assertEqual(doc_tokens, 
                         self.solution_simple_tokenizer_test_data_1)


    def test_collocations_tokenizer(self):
        id_documents = iter_document_json_stream(
            './topik/tests/data/test-data-2', "text")
        ids, doc_text = unzip(id_documents)
        collocations_tokenizer = CollocationsTokenizer(doc_text, 
                                  min_bigram_freq=2, min_trigram_freq=2)
        doc_tokens = next(iter(collocations_tokenizer))
        self.assertEqual(doc_tokens, 
                         self.solution_collocations_tokenizer_test_data_2)

    def test_entities_tokenizer(self):
        id_documents = iter_document_json_stream(
            './topik/tests/data/test-data-2', "text")
        ids, doc_text = unzip(id_documents)
        entities_tokenizer = EntitiesTokenizer(doc_text, 1)
        doc_tokens = next(iter(entities_tokenizer))
        self.assertEqual(doc_tokens, 
                         self.solution_entities_tokenizer_test_data_2)

    def test_mixed_tokenizer(self):
        id_documents = iter_document_json_stream(
            './topid/tests/data/test-data-2', "text")
        ids, doc_text = unzip(id_documents)
        mixed_tokenizer = MixedTokenizer(doc_text)
        doc_tokens = next(iter(mixed_tokenizer))
        self.assertEqual(doc_tokens, 
                         self.solution_mixed_tokenizer_test_data_2)


if __name__ == '__main__':
    unittest.main()
