from six.moves import UserDict
from functools import partial

from topik.singleton_registry import _base_register_decorator


# This subclass serves to establish a new singleton instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class VectorizerRegistry(UserDict, object):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}

    def __init__(self, *args, **kwargs):
        self.__dict__ = self.__shared_state
        super(VectorizerRegistry, self).__init__(*args, **kwargs)


# a nicer, more pythonic handle to our singleton instance
registered_vectorizers = VectorizerRegistry()

# fill in the registration function
register = partial(_base_register_decorator, registered_vectorizers)


def vectorize(corpus, method="bag_of_words", **kwargs):
    """Represent documents as vectors in word-space.

    Note: bag-of-words model is implicitly used when no additional
    vectorization is called.
    """
    return registered_vectorizers[method](corpus, **kwargs)
