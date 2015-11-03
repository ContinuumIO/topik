from ._registry import register

@register
def lda_vis(model_data):
    """Designed to work with to_py_lda_vis() in the model classes."""
    from pyLDAvis import prepare, show
    model_vis_data = prepare(**model_data)
    if mode == 'save_html' and filename:
        save_html(model_vis_data, filename)
    else:
        show(model_vis_data)