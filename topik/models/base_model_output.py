from collections import Counter

import numpy as np
import pandas as pd


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

    def get_top_words(self, topn):
        top_words = []
        # each "topic" is a row of the dz matrix
        for topic in self._doc_topic_matrix.T:
            word_ids = np.argpartition(topic, -topn)[-topn:]
            word_ids = reversed(word_ids[np.argsort(topic[word_ids])])
            top_words.append([(topic[word_id], self._corpus.get_id2word_dict()[word_id]) for word_id in word_ids])
        return top_words

    def term_topic_matrix(self):
        self._corpus.term_topic_matrix

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

    def doc_topic_dists(self):
        return self._doc_topic_matrix

