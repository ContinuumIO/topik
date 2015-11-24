# these imports register the functions with the
# registered_tokenizers function registry.
from .entities import entities, mixed
from .simple import simple
from .ngrams import ngrams

from ._registry import registered_tokenizers, register, tokenize
