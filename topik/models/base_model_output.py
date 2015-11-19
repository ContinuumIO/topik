import json
import numpy as np


class TopicModelResultBase(object):
    """Abstract base class for topic models.

    Ensures consistent interface across models, for base result display capabilities.

    Attributes
    ----------
    _doc_topic_matrix : mapping of document ids to weights for topic indices
                        matrix storing the relative topic weights for each document
    _topic_term_matrix : mapping of terms to each topic
    """
    def __init__(self, doc_topic_matrix, topic_term_matrix):
        self._doc_topic_matrix = doc_topic_matrix
        self._topic_term_matrix = topic_term_matrix

    @property
    def topic_term_matrix(self):
        return self._topic_term_matrix

    def _get_term_data(self):
        vocab = self._get_vocab()
        tf = self._get_term_frequency()
        ttd = self._get_topic_term_dists()
        term_data_df = ttd
        term_data_df['term_frequency'] = tf
        term_data_df['term'] = vocab
        return term_data_df

    def _get_doc_data(self):
        doc_data_df = self._get_doc_topic_dists()
        doc_data_df['doc_length'] = self._get_doc_lengths()
        return doc_data_df

    @property
    def doc_topic_matrix(self):
        return self._doc_topic_matrix

