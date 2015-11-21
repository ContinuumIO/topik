import os

import nose.tools as nt

from topik.visualizers.termite_plot import _get_top_words, _termite_data, termite
from topik.models.tests.test_data import test_model_output

TOP_WORDS = 5
module_path = os.path.dirname(__file__)


def test_top_words():
    top_words = _get_top_words(test_model_output, TOP_WORDS)
    nt.assert_equal(len(top_words), 2)  # each entry is a topic
    nt.assert_equal(len(top_words[1]), TOP_WORDS)
    # ensure that word list is sorted prooperly, with descending weights
    nt.assert_less(top_words[0][1][0], top_words[0][0][0])
    nt.assert_less(top_words[0][-1][0], top_words[0][-2][0])


def test_termite_pandas_output():
    data = _termite_data(test_model_output, topn=TOP_WORDS)
    nt.assert_false(data.empty)
    nt.assert_equal(len(data.columns), 3)
    nt.assert_equal(len(data), TOP_WORDS * 2)

def test_termite():
    data = _termite_data(test_model_output, topn=TOP_WORDS)
    termite_plot = termite(data, "My lda results")
    termite_plot.save(os.path.join(module_path, 'termite_plot.html'))
    nt.assert_true(os.path.isfile(os.path.join(module_path, 'termite_plot.html')))
    os.remove(os.path.join(module_path, 'termite_plot.html'))