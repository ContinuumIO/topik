from functools import partial

from topik.singleton_registry import BaseRegistry, base_register_decorator

# This subclass serves to establish a new singleon instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class VisualizerRegistry(BaseRegistry):
    pass

# a nicer, more pythonic handle to our singleton instance
registered_visualizers = VisualizerRegistry()


# fill in the registration function
register = partial(base_register_decorator, VisualizerRegistry)


# this function is the primary API for people using any registered functions.
def visualize(model_data, method="termite", **kwargs):
    """
    model_data: the ModelOutputBase-derived output of a modeling function
    method: the string identifier of the visualizer function to use.  Available
        methods are keys in the registered_visualizers dictionary.
    kwargs: arbitrary extra parameters to be passed through to visualizer function.
    """
    return registered_visualizers[method](model_data, **kwargs)
