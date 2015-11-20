from collections import Counter

import json
import numpy as np
import pandas as pd

def _get_vocab(vectorized_corpus):
    return pd.Series(vectorized_corpus.id_term_map)

def _get_term_frequency(vectorized_corpus):
    tf = Counter()
    print("TF:")
    print(list(iter(vectorized_corpus)))
    [tf.update(dict(doc)) for doc_id, doc in vectorized_corpus]
    print(dict(tf))
    return dict(tf)

def _get_doc_lengths(vectorized_corpus):
    return pd.Series(vectorized_corpus.document_term_counts)

class ModelOutput(object):
    """Abstract base class for topic models.

    Ensures consistent interface across models, for base result display capabilities.

    Attributes
    ----------
    _doc_topic_matrix : mapping of document ids to weights for topic indices
                        matrix storing the relative topic weights for each document
    _topic_term_matrix : mapping of terms to each topic
    """
    def __init__(self, vectorized_corpus=None, model_func=None,
                 term_data=None, doc_data=None):
                 #doc_topic_matrix, topic_term_matrix):
        #self._doc_topic_matrix = doc_topic_matrix
        #self._topic_term_matrix = topic_term_matrix
        if vectorized_corpus and model_func:
            self._vocab = vectorized_corpus.id_term_map
            self._term_frequency = _get_term_frequency(vectorized_corpus)
            self._topic_term_matrix, self._doc_topic_matrix = model_func(vectorized_corpus)

            #self._term_data = self._get_term_data()

            self._doc_lengths = _get_doc_lengths(vectorized_corpus)

            #self._doc_data = self._get_doc_data()
        elif term_data and doc_data:
            pass
        else:
            raise ValueError("Must provide either vectorized corpus and model func, "
                             "or term data and doc data.")

    '''
    def _get_term_data(self):
        vocab = self._vocab
        tf = self._term_frequency
        ttd = self._topic_term_dists
        term_data_df = ttd
        term_data_df['term_frequency'] = tf
        term_data_df['term'] = vocab
        return term_data_df

    def _get_doc_data(self):
        doc_data_df = self._doc_topic_dists
        doc_data_df['doc_length'] = self._doc_lengths
        return doc_data_df
    '''

    '''
    @property
    def term_data(self):
        return self._term_data

    @property
    def doc_data(self):
        return self._doc_data
    '''

    @property
    def vocab(self):
        return self._vocab

    @property
    def term_frequency(self):
        return self._term_frequency

    @property
    def topic_term_matrix(self):
        return self._topic_term_matrix

    @property
    def doc_lengths(self):
        return self._doc_lengths

    @property
    def doc_topic_matrix(self):
        return self._doc_topic_matrix


