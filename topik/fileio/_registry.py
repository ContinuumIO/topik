from functools import partial
from six.moves import UserDict

from topik.singleton_registry import _base_register_decorator


class InputRegistry(UserDict, object):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        super(InputRegistry, self).__init__()


class OutputRegistry(UserDict, object):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        super(OutputRegistry, self).__init__()


# a nicer, more pythonic handle to our singleton instance
registered_inputs = InputRegistry()
registered_outputs = OutputRegistry()


# fill in the registration function
register_input = partial(_base_register_decorator, registered_inputs)
register_output = partial(_base_register_decorator, registered_outputs)
