# these imports register the functions with the
# registered_models function registry.
from .lda import _LDA
from .plsa import _PLSA

from ._registry import registered_models, register, run_model
