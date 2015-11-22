from six.moves import UserDict
from functools import partial

from topik.singleton_registry import _base_register_decorator


# This subclass serves to establish a new singleon instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class TokenizerRegistry(UserDict, object):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self, *args, **kwargs):
        self.__dict__ = self.__shared_state
        super(TokenizerRegistry, self).__init__(*args, **kwargs)


# a nicer, more pythonic handle to our singleton instance
registered_tokenizers = TokenizerRegistry()

# fill in the registration function
register = partial(_base_register_decorator, registered_tokenizers)


def tokenize(corpus, method="simple", **kwargs):
    """Break documents up into component words, optionally eliminating stopwords.

    Output from this function is used as input to vectorization steps.

    raw_data: iterable corpus object containing the text to be processed.
        Each iteration call should return a new document's content.
    method: string id of tokenizer to use.  For keys, see
        topik.tokenizers.registered_tokenizers (which is a dictionary of functions)
    kwargs: arbitrary dicionary of extra parameters.
    """
    return registered_tokenizers[method](corpus, **kwargs)
