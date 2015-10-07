from abc import ABCMeta, abstractmethod
import logging

import pandas as pd
from six import with_metaclass

# doctest-only imports
from topik.readers import read_input
from topik.tests import test_data_path
from topik.intermediaries.persistence import Persistor

registered_models = {}

def register_model(cls):
    global registered_models
    if cls.__name__ not in registered_models:
        registered_models[cls.__name__] = cls
    return cls


class TopicModelBase(with_metaclass(ABCMeta)):
    corpus = None

    @abstractmethod
    def get_top_words(self, topn):
        """Method should collect top n words per topic, translate indices/ids to words.

        Return a list of lists of tuples:
        - outer list: topics
        - inner lists: length topn collection of (weight, word) tuples
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, filename, saved_data):
        self.persistor.store_model(self.get_model_name_with_parameters(),
                                   {"class": self.__class__.__name__,
                                    "saved_data": saved_data})
        self.corpus.save(filename)

    @abstractmethod
    def get_model_name_with_parameters(self):
        raise NotImplementedError

    @abstractmethod
    def _get_term_data(self):
        raise NotImplementedError

    @abstractmethod
    def _get_vocab(self):
        raise NotImplementedError

    @abstractmethod
    def _get_term_frequency(self):
        raise NotImplementedError

    @abstractmethod
    def _get_topic_term_dists(self):
        raise NotImplementedError

    @abstractmethod
    def _get_doc_data(self):
        raise NotImplementedError

    @abstractmethod
    def _get_doc_topic_dists(self):
        raise NotImplementedError

    @abstractmethod
    def _get_doc_lengths(self):
        raise NotImplementedError

    def to_py_lda_vis(self):
        doc_data_df = self._get_doc_data()
        term_data_df = self._get_term_data()

        model_lda_vis_data = {  'vocab': term_data_df['token'],
                                'term_frequency': term_data_df['doc_count'],
                                'topic_term_dists': term_data_df.iloc[:,2:].T,
                                'doc_topic_dists': doc_data_df.iloc[:,:-1],
                                'doc_lengths': doc_data_df['doc_length']}
        return model_lda_vis_data

    def termite_data(self, topn_words=15):
        """Generate the pandas dataframe input for the termite plot.

        Parameters
        ----------
        topn_words: int
            number of words to include from each topic

        >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
        >>> processed_data = raw_data.tokenize()  # tokenize returns a DigestedDocumentCollection
        >>> model = registered_models["LDA"](processed_data, ntopics=3)
        >>> model.termite_data(15)
        
        """
        from itertools import chain
        return pd.DataFrame(list(chain.from_iterable([{"topic": topic_id, "weight": weight, "word": word}
                                                      for (weight, word) in topic]
                                                     for topic_id, topic in enumerate(self.get_top_words(topn_words)))))

    @property
    def persistor(self):
        return self.corpus.persistor


def load_model(filename, model_name):
    """Loads a JSON file containing instructions on how to load model data.

    Returns a TopicModelBase-derived object."""
    p = Persistor(filename)
    if model_name in p.list_available_models():
        data_dict = p.get_model_details(model_name)
        model = registered_models[data_dict['class']](**data_dict["saved_data"])
    else:
        raise NameError("Model name {} has not yet been created.".format(model_name))
    return model
