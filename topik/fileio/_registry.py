from functools import partial

from topik.singleton_registry import _base_register_decorator


class InputRegistry(dict):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state


class OutputRegistry(dict):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state


# a nicer, more pythonic handle to our singleton instance
registered_inputs = InputRegistry()
registered_outputs = OutputRegistry()


# fill in the registration function
register_input = partial(_base_register_decorator, registered_inputs)
register_output = partial(_base_register_decorator, registered_outputs)
