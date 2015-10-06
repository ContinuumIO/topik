import unittest

from topik.models import registered_models, PLSA
from topik.readers import read_input
from topik.tests import test_data_path


class TestPLSA(unittest.TestCase):
    def setUp(self):
        test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        self.processed_data = test_raw_data.tokenize()

    def test_train(self):
        plsa = PLSA(self.processed_data, ntopics=5)
        plsa.train()
        assert(plsa.likelihood != 0)  # TODO: this is a really poor test, but at least makes sure that things run.

    def test_registration(self):
        assert("PLSA" in registered_models)
