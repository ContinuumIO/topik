import os
import unittest

from topik.readers import iter_document_json_stream
from topik.tokenizers import SimpleTokenizer
from topik.vectorizers import CorpusBOW
from topik.models import LDA
from topik.utils import unzip

# sample data files are located in the same folder
module_path = os.path.dirname(__file__)

class TestModels(unittest.TestCase):

    def setUp(self):
        id_documents =  iter_document_json_stream(
                os.path.join(module_path,'data/test-data-1'), "text")
        ids, doc_text = unzip(id_documents)
        my_corpus = SimpleTokenizer(doc_text)
        corpus_bow = CorpusBOW(my_corpus)
        corpus_bow.save_dict(os.path.join(module_path, 'test.dict'))
        corpus_bow.serialize(os.path.join(module_path, 'test.mm'))

    def tearDown(self):
        os.remove(os.path.join(module_path, 'test.dict'))
        os.remove(os.path.join(module_path, 'test.mm'))
        os.remove(os.path.join(module_path, 'test.model'))

    def test_lda(self):
        my_lda = LDA("test.mm", "test.dict", ntopics=3)
        my_lda.save(os.path.join(module_path, 'test.model'))
        top_words = my_lda.get_top_words(15)
        self.assertEqual(len(top_words), 3)
        self.assertEqual(len(top_words[1]), 15)

        my_lda.termite_data(os.path.isfile(os.path.join(module_path, 'test_termite.csv')))

        self.assertTrue(os.path.isfile(os.path.join(module_path, 'test.model')))
        self.assertTrue(os.path.isfile(os.path.join(module_path, 'test_termite.model')))

if __name__ == '__main__':
    unittest.main()
