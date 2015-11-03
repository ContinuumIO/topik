# these imports register the functions with the
# registered_tokenizers function registry.
from .entities import entities
from .simple import simple
from .ngrams import ngrams

from ._registry import registered_tokenizers, tokenize