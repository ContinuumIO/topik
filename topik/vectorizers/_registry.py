from functools import partial

from topik.singleton_registry import _base_register_decorator


class VectorizerRegistry(dict):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state


# a nicer, more pythonic handle to our singleton instance
registered_vectorizers = VectorizerRegistry()


# fill in the registration function
register = partial(_base_register_decorator, registered_vectorizers)


def vectorize(corpus, method="tfidf", **kwargs):
    """Represent documents as vectors in word-space.

    Note: bag-of-words model is implicitly used when no additional
    vectorization is called.
    """
    return registered_vectorizers[method](corpus, **kwargs)
