from .lda import LDA
from .plsa import PLSA

from .model_base import load_model
from ._registered_models import ModelRegistry

registered_models = ModelRegistry()