from functools import partial

from topik.singleton_registry import _base_register_decorator
from .base_model_output import load_model


# This subclass serves to establish a new singleton instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class ModelRegistry(dict):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state

# a nicer, more pythonic handle to our singleton instance
registered_models = ModelRegistry()


# fill in the registration function
register = partial(_base_register_decorator, registered_models)


# this function is the primary API for people using any registered functions.
def run_model(model_name, input_data, **kwargs):
    return ModelRegistry()[model_name](input_data, **kwargs)
