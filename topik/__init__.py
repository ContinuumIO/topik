from topik.fileio.readers import read_input
from .models import registered_models, load_model
from .fileio.raw_corpus import registered_outputs, load_persisted_corpus

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
