"""
This file is concerned with providing a simple interface for data stored in
Elasticsearch.  The class(es) defined here are fed into the preprocessing step.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
import logging
import time

from six import with_metaclass

from gensim.corpora.dictionary import Dictionary

from topik.fileio.persistence import Persistor
from topik.tokenizers import tokenizer_methods
from topik.fileio.tokenized_corpus import TokenizedCorpus


registered_outputs = {}

def register_output(cls):
    global registered_outputs
    if cls.class_key() not in registered_outputs:
        registered_outputs[cls.class_key()] = cls
    return cls


def _get_hash_identifier(input_data, field_to_hash):
    return hash(input_data[field_to_hash])


def _get_parameters_string(**kwargs):
    """Used to create identifiers for output"""
    id = ''.join('{}={}_'.format(key, val) for key, val in sorted(kwargs.items()))
    return id[:-1]


class OutputInterface(with_metaclass(ABCMeta)):
    def __init__(self):
        super(OutputInterface, self).__init__()
        self.persistor = Persistor()

    @classmethod
    @abstractmethod
    def class_key(cls):
        """Implement this method to return the string ID with which to store your class."""
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        """This is expected to iterate over your data, returning tuples of (doc_id, <selected field>)"""
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def get_generator_without_id(self, field=None):
        """Returns a generator that yields field content without doc_id associate"""
        raise NotImplementedError

    @abstractmethod
    def get_date_filtered_data(self, start, end, field):
        raise NotImplementedError

    @abstractproperty
    def filter_string(self):
        raise NotImplementedError

    def save(self, filename, saved_data=None):
        """Persist this object to disk somehow.

        You can save your data in any number of files in any format, but at a minimum, you need one json file that
        describes enough to bootstrap the loading prcess.  Namely, you must have a key called 'class' so that upon
        loading the output, the correct class can be instantiated and used to load any other data.  You don't have
        to implement anything for saved_data, but it is stored as a key next to 'class'.

        """
        self.persistor.store_corpus({"class": self.__class__.class_key(), "saved_data": saved_data})
        self.persistor.persist_data(filename)

    def synchronize(self, max_wait, field):
        """By default, operations are synchronous and no additional wait is
        necessary.  Data sources that are asynchronous (ElasticSearch) may
        use this function to wait for "eventual consistency" """
        pass


def load_persisted_corpus(filename):
    corpus_dict = Persistor(filename).get_corpus_dict()
    return registered_outputs[corpus_dict['class']](**corpus_dict["saved_data"])
