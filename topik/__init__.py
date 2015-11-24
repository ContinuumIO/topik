from __future__ import absolute_import, print_function
import logging

from topik.fileio import TopikProject, read_input
from topik.tokenizers import tokenize
from topik.vectorizers import vectorize
from topik.transformers import transform
from topik.models import run_model
from topik.visualizers import visualize

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.WARNING)
