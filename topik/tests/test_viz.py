import unittest
import os

from topik.viz import Termite

module_path = os.path.dirname(__file__)


class TestTokenizers(unittest.TestCase):

    def test_termite(self):
        termite = Termite(os.path.join(module_path, 'data/termite.csv' ), "My lda results")
        termite.plot(os.path.join(module_path, 'termite_plot.html'))

        self.assertTrue(os.path.isfile(os.path.join(module_path, 'termite_plot.html')))
