from __future__ import absolute_import, print_function
import logging

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)
