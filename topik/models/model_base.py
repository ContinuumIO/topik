from abc import ABCMeta, abstractmethod
from collections import Counter
import logging

import pandas as pd
from six import with_metaclass

# doctest-only imports
from topik.readers import read_input
from topik.tests import test_data_path
from topik.intermediaries.persistence import Persistor

registered_models = {}

def register_model(cls):
    """Decorator function to register new model with global registry of models"""
    global registered_models
    if cls.__name__ not in registered_models:
        registered_models[cls.__name__] = cls
    return cls


class TopicModelBase(with_metaclass(ABCMeta)):
    """Abstract base class for topic models.

    Ensures consistent interface across models, for base result display capabilities.

    Attributes
    ----------
    _corpus : topik.intermediaries.digested_document_collection.DigestedDocumentCollection-derived object
        The input data for this model
    _persistor : topik.intermediaries.persistor.Persistor object
        The object responsible for persisting the state of this model to disk.  Persistor saves metadata
        that instructs load_model how to load the actual data.
    """
    _corpus = None

    @abstractmethod
    def get_top_words(self, topn):
        """Abstract method.  Implementations should collect top n words per topic, translate indices/ids to words.

        Returns
        -------
        list of lists of tuples:
            * outer list: topics
            * inner lists: length topn collection of (weight, word) tuples
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, filename, saved_data):
        """Abstract method.  Persist the model metadata and data to disk.

        Implementations should both save their important data do disk with some known keyword
        (perhaps as filename or server address details), and pass a dictionary to saved_data.
        The contents of this dictionary will be passed to the class' constructor as **kwargs.

        Be sure to either call super(YourClass, self).save(filename, saved_data) or otherwise
        duplicate the base level of functionality here.

        Parameters
        ----------
        filename : str
            The filename of the JSON file to be saved, containing model and corpus metadata
            that allow for reconstruction
        saved_data : dict
            Dictionary of metadata that will be fed to class __init__ method at load time.
            This should include such things as number of topics modeled, binary filenames,
            and any other relevant model parameters to recreate your current model.
        """
        self._persistor.store_model(self.get_model_name_with_parameters(),
                                   {"class": self.__class__.__name__,
                                    "saved_data": saved_data})
        self._corpus.save(filename)

    @abstractmethod
    def get_model_name_with_parameters(self):
        """Abstract method.  Primarily internal function, used to name configurations in persisted metadata for later retrieval."""
        raise NotImplementedError

    def _get_term_data(self):
        vocab = self._get_vocab()
        tf = self._get_term_frequency()
        ttd = self._get_topic_term_dists()
        term_data_df = ttd
        term_data_df['term_frequency'] = tf
        term_data_df['term'] = vocab
        return term_data_df

    def _get_vocab(self):
        return pd.Series(dict(self._corpus._dict.items()))

    def _get_term_frequency(self):
        tf = Counter()
        [tf.update(dict(doc)) for doc in self._corpus]
        # TODO update term documents in intermediate store
        return pd.Series(dict(tf))

    def _get_doc_data(self):
        doc_data_df = self._get_doc_topic_dists()
        doc_data_df['doc_length'] = self._get_doc_lengths()
        return doc_data_df

    def _get_doc_lengths(self):
        id_index, doc_lengths = zip(*[(id, len(doc)) for id, doc in list(
                                                        self._corpus._corpus)])
        return pd.Series(doc_lengths, index=id_index)

    @abstractmethod
    def _get_topic_term_dists(self):
        raise NotImplementedError

    @abstractmethod
    def _get_doc_topic_dists(self):
        raise NotImplementedError

    def to_py_lda_vis(self):
        doc_data_df = self._get_doc_data()
        term_data_df = self._get_term_data()

        model_lda_vis_data = {  'vocab': term_data_df['term'],
                                'term_frequency': term_data_df['term_frequency'],
                                'topic_term_dists': term_data_df.iloc[:,:-2].T,
                                'doc_topic_dists': doc_data_df.iloc[:,:-1],
                                'doc_lengths': doc_data_df['doc_length']}
        return model_lda_vis_data

    def termite_data(self, topn_words=15):
        """Generate the pandas dataframe input for the termite plot.

        Parameters
        ----------
        topn_words : int
            number of words to include from each topic

        Examples
        --------
        >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
        >>> processed_data = raw_data.tokenize()  # tokenize returns a DigestedDocumentCollection
        >>> # must set seed so that we get same topics each run
        >>> import random
        >>> import numpy
        >>> random.seed(42)
        >>> numpy.random.seed(42)
        >>> model = registered_models["LDA"](processed_data, ntopics=3)
        >>> model.termite_data(5)
            topic    weight         word
        0       0  0.005337           nm
        1       0  0.005193         high
        2       0  0.004622        films
        3       0  0.004457       matrix
        4       0  0.004194     electron
        5       1  0.005109   properties
        6       1  0.004654         size
        7       1  0.004539  temperature
        8       1  0.004499           nm
        9       1  0.004248   mechanical
        10      2  0.007994         high
        11      2  0.006458           nm
        12      2  0.005717         size
        13      2  0.005399    materials
        14      2  0.004734        phase

        """
        from itertools import chain
        return pd.DataFrame(list(chain.from_iterable([{"topic": topic_id, "weight": weight, "word": word}
                                                      for (weight, word) in topic]
                                                     for topic_id, topic in enumerate(self.get_top_words(topn_words)))))

    @property
    def _persistor(self):
        return self._corpus.persistor


def load_model(filename, model_name):
    """Loads a JSON file containing instructions on how to load model data.

    Returns
    -------
    TopicModelBase-derived object
    """
    p = Persistor(filename)
    if model_name in p.list_available_models():
        data_dict = p.get_model_details(model_name)
        model = registered_models[data_dict['class']](**data_dict["saved_data"])
    else:
        raise NameError("Model name {} has not yet been created.".format(model_name))
    return model
