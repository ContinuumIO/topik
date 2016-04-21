import pandas as pd
import logging
from ._registry import register

def _to_py_lda_vis(modeled_corpus):
    vocab = pd.Series(modeled_corpus.vocab)
    term_frequency = pd.Series(modeled_corpus.term_frequency)
    topic_term_matrix = pd.DataFrame(modeled_corpus.topic_term_matrix)

    doc_lengths = pd.Series(modeled_corpus.doc_lengths)
    doc_topic_matrix = pd.DataFrame(modeled_corpus.doc_topic_matrix).T

    term_data = topic_term_matrix
    term_data['term_frequency'] = term_frequency
    term_data['vocab'] = vocab

    doc_data = doc_topic_matrix
    doc_data['doc_length'] = doc_lengths

    model_vis_data = {  'vocab': term_data['vocab'],
                            'term_frequency': term_data['term_frequency'],
                            'topic_term_dists': term_data.iloc[:,:-2].T,
                            'doc_topic_dists': doc_data.iloc[:,:-1],
                            'doc_lengths': doc_data['doc_length']}
    return model_vis_data

@register
def lda_vis(modeled_corpus, mode='show', filename=None):
    """Designed to work with to_py_lda_vis() in the model classes."""
    from pyLDAvis import prepare, show, save_html

    model_vis_data = _to_py_lda_vis(modeled_corpus)
    prepared_model_vis_data = prepare(**model_vis_data)
    if mode == 'save_html' and filename:
        logging.info("Saving pyLDAVis to {}".format(filename))
        save_html(prepared_model_vis_data, filename)
    else:
        show(prepared_model_vis_data, ip="0.0.0.0", port=8888)

