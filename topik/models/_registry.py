from six.moves import UserDict
from functools import partial

from topik.singleton_registry import _base_register_decorator


# This subclass serves to establish a new singleton instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class ModelRegistry(UserDict, object):
    """Uses Borg design pattern.  Core idea is that there is a global registry for each step's
    possible methods
    """
    __shared_state = {}
    def __init__(self, *args, **kwargs):
        self.__dict__ = self.__shared_state
        super(ModelRegistry, self).__init__(*args, **kwargs)


# a nicer, more pythonic handle to our singleton instance
registered_models = ModelRegistry()


# fill in the registration function
register = partial(_base_register_decorator, registered_models)


# this function is the primary API for people using any registered functions.
def run_model(input_data, model_name='lda', ntopics=3, **kwargs):
    return registered_models[model_name](input_data, ntopics, **kwargs)
