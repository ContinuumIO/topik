import os

import nose.tools as nt

from topik.visualizers import termite

# TODO: write some fake data in here.
data = {}

module_path = os.path.dirname(__file__)


def test_termite():
    termite_plot = termite(data, "My lda results")
    termite_plot.save(os.path.join(module_path, 'termite_plot.html'))
    nt.assert_true(os.path.isfile(os.path.join(module_path, 'termite_plot.html')))
    os.remove(os.path.join(module_path, 'termite_plot.html'))