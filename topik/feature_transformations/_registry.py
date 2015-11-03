from functools import partial

from topik.singleton_registry import BaseRegistry, base_register_decorator


# This subclass serves to establish a new singleon instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class TransformerRegistry(BaseRegistry):
    pass


# a nicer, more pythonic handle to our singleton instance
registered_transformers = TransformerRegistry()


# fill in the registration function
register = partial(base_register_decorator, TransformerRegistry)


# this function is the primary API for people using any registered functions.
def run_model(model_name, input_data, **kwargs):
    return TransformerRegistry()[model_name](input_data, **kwargs)
