from six.moves import UserDict
from functools import partial

from topik.singleton_registry import _base_register_decorator


class TransformerRegistry(UserDict):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state


# a nicer, more pythonic handle to our singleton instance
registered_transformers = TransformerRegistry()


# fill in the registration function
register = partial(_base_register_decorator, registered_transformers)


# this function is the primary API for people using any registered functions.
def transform(tranformation_name, input_data, **kwargs):
    return registered_transformers[tranformation_name](input_data, **kwargs)
