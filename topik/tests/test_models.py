import os
import unittest
from abc import ABCMeta, abstractmethod

from six import with_metaclass

from topik.readers import read_input
from topik.preprocessing import preprocess
from topik.models import LDA, PLSA

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)

NTOPICS = 3
MODEL_SAVE_FILENAME = 'test.model'
MODEL_LOAD_FILENAME = 'test.model'  # This one is harder: may be different for each model, but should be static and known good


class ModelBase(with_metaclass(ABCMeta)):
    def setUp(self):
        raw_data = read_input(
                source=os.path.join(module_path, 'data/test_data_json_stream.json'),
                content_field="abstract")
        self.digested_data = preprocess(raw_data)
        self.model = self._train_model()

    def tearDown(self):
        if os.path.exists(os.path.join(module_path, MODEL_SAVE_FILENAME)):
            os.remove(os.path.join(module_path, MODEL_SAVE_FILENAME))

    @abstractmethod
    def _train_model(self):
        raise NotImplementedError

    @abstractmethod
    def _load_saved_model(self, filename):
        raise NotImplementedError

    def test_save_data(self):
        self.model.save(os.path.join(module_path, MODEL_SAVE_FILENAME))
        self.assertTrue(os.path.isfile(os.path.join(module_path, MODEL_SAVE_FILENAME)))

    def test_load_data(self):
        """NOTE: This test depends on save data succeeding!  May want to have static known-good data instead."""
        self.model.save(os.path.join(module_path, MODEL_SAVE_FILENAME))
        model = self._load_saved_model(MODEL_LOAD_FILENAME)
        self.assertGreater(model.get_top_words(5), 0)

    def test_top_words(self):
        top_words = self.model.get_top_words(15)
        self.assertEqual(len(top_words), 3)
        self.assertEqual(len(top_words[1]), 15)

    def test_termite_output(self):
        self.model.termite_data(os.path.join(module_path, 'test_termite.csv'))
        self.assertTrue(os.path.isfile(os.path.join(module_path, 'test_termite.csv')))


class TestLDA(ModelBase, unittest.TestCase):
    def _train_model(self):
        return LDA(self.digested_data, ntopics=NTOPICS)

    def _load_saved_model(self, filename):
        return LDA(fname=filename)


class TestPLSA(ModelBase, unittest.TestCase):
    def _train_model(self):
        return PLSA(self.digested_data, topics=NTOPICS)

    def _load_saved_model(self, filename):
        return PLSA(fname=filename)


if __name__ == '__main__':
    unittest.main()
