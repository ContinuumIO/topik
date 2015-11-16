from ._registry import register

def to_py_lda_vis(token_data, model_data):
    doc_data_df = self._get_doc_data()
    term_data_df = self._get_term_data()

    model_lda_vis_data = {  'vocab': term_data_df['term'],
                            'term_frequency': term_data_df['term_frequency'],
                            'topic_term_dists': term_data_df.iloc[:,:-2].T,
                            'doc_topic_dists': doc_data_df.iloc[:,:-1],
                            'doc_lengths': doc_data_df['doc_length']}
    return model_lda_vis_data


@register
def lda_vis(model_data):
    """Designed to work with to_py_lda_vis() in the model classes."""
    from pyLDAvis import prepare, show
    model_vis_data = prepare(**model_data)
    if mode == 'save_html' and filename:
        save_html(model_vis_data, filename)
    else:
        show(model_vis_data)

