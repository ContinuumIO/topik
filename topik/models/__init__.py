# these imports register the functions with the
# registered_models function registry.
from .lda import lda
from .plsa import plsa

from ._registry import registered_models, register, run_model
