


@register_visualizer
def plot_lda_vis(model_data):
    """Designed to work with to_py_lda_vis() in the model classes."""
    from pyLDAvis import prepare, show
    model_vis_data = prepare(**model_data)
    show(model_vis_data)