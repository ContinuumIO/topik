# these imports register the functions with the
# registered_models function registry.
from .lda import LDA
from .plsa import PLSA

from ._registry import registered_models, run_model
