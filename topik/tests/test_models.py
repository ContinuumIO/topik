import os
import unittest

from topik.readers import iter_document_json_stream
from topik.preprocessing import preprocess
from topik.models import LDA
from topik.utils import unzip

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)


class TestModels(unittest.TestCase):

    def setUp(self):
        raw_data = iter_document_json_stream(
                os.path.join(module_path, 'data/test-data-1.json'), "text")
        self.digested_data = preprocess(raw_data)

    def tearDown(self):
        if os.path.exists(os.path.join(module_path, 'test.model')):
            os.remove(os.path.join(module_path, 'test.model'))

    def test_lda(self):
        my_lda = LDA(self.digested_data, ntopics=3)
        my_lda.save(os.path.join(module_path, 'test.model'))
        top_words = my_lda.get_top_words(15)
        self.assertEqual(len(top_words), 3)
        self.assertEqual(len(top_words[1]), 15)

        my_lda.termite_data(os.path.isfile(os.path.join(module_path, 'test_termite.csv')))

        self.assertTrue(os.path.isfile(os.path.join(module_path, 'test.model')))
        self.assertTrue(os.path.isfile(os.path.join(module_path, 'test_termite.model')))

if __name__ == '__main__':
    unittest.main()
