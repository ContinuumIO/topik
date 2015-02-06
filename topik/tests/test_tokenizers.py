import unittest

from topik.utils import head
from topik.readers import iter_document_json_stream
from topik.tokenizers import SimpleTokenizer, CollocationsTokenizer, EntitiesTokenizer, MixedTokenizer


class TestTokenizers(unittest.TestCase):
    def setUp(self):
        self.solution_simple_tokenizer_test_data_1 = [[u'interstellar', u'incredible', u'visuals', u'score', u'acting',
                                                       u'amazing', u'plot', u'definitely', u'original', u've', u'seen']]

        self.solution_collocations_tokenizer_test_data_2 = [
            [u'paper', u'simple', u'rapid', u'solution', u'phase', u'chemical',
             u'reduction', u'method', u'inert', u'gas', u'protection', u'preparing',
             u'stable', u'copper', u'nanoparticle', u'colloid', u'average',
             u'particle', u'size', u'narrow', u'size_distribution', u'synthesis_route',
             u'ascorbic_acid', u'natural', u'vitamin', u'serves', u'reducing', u'agent',
             u'antioxidant', u'reduce', u'copper', u'salt', u'precursor', u'effectively', u'prevent',
             u'general', u'oxidation', u'process', u'occurring', u'newborn',
             u'nanoparticles', u'xrd', u'vis', u'confirm', u'formation', u'pure', u'face', u'centered',
             u'cubic', u'fcc', u'copper', u'nanoparticles', u'excellent', u'antioxidant', u'ability', u'ascorbic_acid']]

        self.solution_entities_tokenizer_test_data_2 = [[u'rapid_solution_phase_chemical_reduction_method',
                                                         u'inert_gas_protection', u'stable_copper_nanoparticle_colloid',
                                                         u'average_particle_size', u'narrow_size_distribution',
                                                         u'synthesis_route', u'ascorbic_acid', u'natural_vitamin_c',
                                                         u'vc', u'copper_salt_precursor', u'general_oxidation_process',
                                                         u'newborn_nanoparticles', u'xrd', u'uv_vis',
                                                         u'copper_nanoparticles', u'excellent_antioxidant_ability',
                                                         u'ascorbic_acid']]

        self.solution_mixed_tokenizer_test_data_2 = [
            [u'rapid', u'solution', u'phase', u'chemical', u'reduction', u'method',
             u'inert', u'gas', u'protection', u'stable', u'copper', u'nanoparticle', u'colloid',
             u'average', u'particle', u'size', u'narrow', u'size', u'distribution',
             u'synthesis_route', u'ascorbic_acid', u'natural', u'vitamin', u'c', u'copper',
             u'salt', u'precursor', u'general', u'oxidation', u'process', u'newborn',
             u'nanoparticles', u'xrd', u'vis', u'copper', u'nanoparticles', u'excellent',
             u'antioxidant', u'ability', u'ascorbic_acid']]

    def test_simple_tokenizer(self):
        doc_text = iter_document_json_stream('./topik/tests/data/test-data-1', "text")
        simple_tokenizer = SimpleTokenizer(doc_text)
        doc_tokens = head(simple_tokenizer)

        self.assertEqual(doc_tokens, self.solution_simple_tokenizer_test_data_1)


    def test_collocations_tokenizer(self):
        doc_text = iter_document_json_stream('./topik/tests/data/test-data-2', "text")
        collocations_tokenizer = CollocationsTokenizer(doc_text, min_bigram_freq=2, min_trigram_freq=2)
        doc_tokens = head(collocations_tokenizer)

        self.assertEqual(doc_tokens, self.solution_collocations_tokenizer_test_data_2)

    def test_entities_tokenizer(self):
        doc_text = iter_document_json_stream('./topik/tests/data/test-data-2', "text")
        entities_tokenizer = EntitiesTokenizer(doc_text, 1)
        doc_tokens = head(entities_tokenizer)

        self.assertEqual(doc_tokens, self.solution_entities_tokenizer_test_data_2)

    def test_mixed_tokenizer(self):
        doc_text = iter_document_json_stream('./topik/tests/data/test-data-2', "text")
        mixed_tokenizer = MixedTokenizer(doc_text)
        doc_tokens = head(mixed_tokenizer)

        self.assertEqual(doc_tokens, self.solution_mixed_tokenizer_test_data_2)


if __name__ == '__main__':
    unittest.main()