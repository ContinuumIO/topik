import os

import nose.tools as nt

from topik.vectorizers.vectorizer_output import VectorizerOutput
from topik.visualizers.termite_plot import _get_top_words, _termite_data, termite

TOP_WORDS = 15
# vectorizer output is what establishes numeric term ID to string term relationship
words = ["a", "an", "the", "dog", "weee", "cat", "airplane", "car", "chair", "llama", "winamp",
         "supercomputing", "frank", "dave", "plastic", "fair", "boot", "latch"]
vectorizer_output = VectorizerOutput(id_term_map={id: term for id, term in enumerate(words)},
                                     document_term_counts={"dummy": True},
                                     vectors={"dummy": True})
# randomly generated using _rand_mat function in PLSA model
topic_term_matrix = [[0.052277337534546914, 0.1066431355086033, 0.018247175367870988, 0.09070086890894988,
                      0.12311021307400236, 0.0009719378193282065, 0.009918214640190859, 0.04213800982796174,
                      0.006178942628296582, 0.02230268265995194, 0.12831288061357243, 0.0366960673968944,
                      0.10743138749387472, 0.08357824205328825, 0.026856303023625606, 0.02751901076850404,
                      0.09212830200498516, 0.02498928867555266],
                     [0.01856730303877282, 0.06236486308863291, 0.09572141892249618, 0.06393592714517904,
                      0.03198526233068787, 0.08687484874994925, 0.05714914919400754, 0.05738922769757895,
                      0.03322084140022692, 0.04376919934175664, 0.04526520432541336, 0.0938735020427431,
                      0.020503299460561578, 0.06170749231856758, 0.08089658307160458, 0.06483798601332702,
                      0.013525961368199139, 0.06841193049029544]]


module_path = os.path.dirname(__file__)


def test_top_words():
    top_words = _get_top_words(vectorizer_output, topic_term_matrix, TOP_WORDS)
    nt.assert_equal(len(top_words), 2)  # each entry is a topic
    nt.assert_equal(len(top_words[1]), TOP_WORDS)
    # ensure that word list is sorted prooperly, with descending weights
    nt.assert_less(top_words[0][1][0], top_words[0][0][0])
    nt.assert_less(top_words[0][-1][0], top_words[0][-2][0])


def test_termite_pandas_output():
    data = _termite_data(vectorizer_output, topic_term_matrix, topn=TOP_WORDS)
    nt.assert_false(data.empty)
    nt.assert_equal(len(data.columns), 3)
    nt.assert_equal(len(data), TOP_WORDS * 2)

def test_termite():
    data = _termite_data(vectorizer_output, topic_term_matrix, topn=TOP_WORDS)
    termite_plot = termite(data, "My lda results")
    termite_plot.save(os.path.join(module_path, 'termite_plot.html'))
    nt.assert_true(os.path.isfile(os.path.join(module_path, 'termite_plot.html')))
    os.remove(os.path.join(module_path, 'termite_plot.html'))