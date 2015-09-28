import os
import unittest

from topik.readers import read_input
from topik.preprocessing import preprocess
from topik.models import registered_models, load_model
from topik.intermediaries.persistence import Persistor

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)

NTOPICS = 3
MODEL_SAVE_FILENAME = os.path.join(module_path, 'test.model')


class _ModelBase(object):
    def setUp(self):
        raw_data = read_input(
                source=os.path.join(module_path, 'data/test_data_json_stream.json'),
                content_field="abstract")
        self.digested_data = preprocess(raw_data)
        self.model = registered_models[self.model_name](self.digested_data, ntopics=NTOPICS)

    def tearDown(self):
        import glob
        for f in glob.glob(MODEL_SAVE_FILENAME+"*"):
            os.remove(f)

    def test_save_data(self):
        self.model.save(MODEL_SAVE_FILENAME)
        self.assertTrue(os.path.isfile(MODEL_SAVE_FILENAME))
        self.assertTrue("class" in Persistor(MODEL_SAVE_FILENAME).get_corpus_dict())

    def test_load_data(self):
        """NOTE: This test depends on save data succeeding!  May want to have static known-good data instead."""
        self.model.save(MODEL_SAVE_FILENAME)
        model = load_model(MODEL_SAVE_FILENAME, self.model.get_model_name_with_parameters())
        self.assertGreater(model.get_top_words(5), 0)

    def test_top_words(self):
        top_words = self.model.get_top_words(15)
        self.assertEqual(len(top_words), 3)
        self.assertEqual(len(top_words[1]), 15)

    def test_termite_output(self):
        self.model.termite_data(os.path.join(module_path, 'test_termite.csv'))
        self.assertTrue(os.path.isfile(os.path.join(module_path, 'test_termite.csv')))


class TestLDA(_ModelBase, unittest.TestCase):
    model_name = "LDA"


class TestPLSA(_ModelBase, unittest.TestCase):
    model_name = "PLSA"


if __name__ == '__main__':
    unittest.main()
