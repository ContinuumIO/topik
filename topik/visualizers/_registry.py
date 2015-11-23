from functools import partial

from topik.singleton_registry import _base_register_decorator

# This subclass serves to establish a new singleon instance of functions
#    for this particular step in topic modeling.  No implementation necessary.
class VisualizerRegistry(dict):
    pass

# a nicer, more pythonic handle to our singleton instance
registered_visualizers = VisualizerRegistry()


# fill in the registration function
register = partial(_base_register_decorator, registered_visualizers)


# this function is the primary API for people using any registered functions.
def visualize(modeled_corpus, vis_name="lda_vis", **kwargs):
    """
    model_data: the ModelOutputBase-derived output of a modeling function
    method: the string identifier of the visualizer function to use.  Available
        methods are keys in the registered_visualizers dictionary.
    kwargs: arbitrary extra parameters to be passed through to visualizer function.
    """
    return registered_visualizers[vis_name](modeled_corpus, **kwargs)
