from functools import partial

from topik.singleton_registry import BaseRegistry, _base_register_decorator


# This subclass serves to establish a new singleton instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class ModelRegistry(BaseRegistry):
    pass


# a nicer, more pythonic handle to our singleton instance
registered_models = ModelRegistry()


# fill in the registration function
register = partial(_base_register_decorator, ModelRegistry)


# this function is the primary API for people using any registered functions.
def run_model(model_name, input_data, **kwargs):
    return ModelRegistry()[model_name](input_data, **kwargs)
