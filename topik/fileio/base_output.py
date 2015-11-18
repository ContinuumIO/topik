from abc import ABCMeta, abstractmethod

from six import with_metaclass
import jsonpickle

from ._registry import registered_outputs


class OutputInterface(with_metaclass(ABCMeta)):
    def __init__(self, *args, **kwargs):
        super(OutputInterface, self).__init__( *args, **kwargs)
        # should be an iterable with each member having (id, text)
        self.corpus = None
        # should be a dictionary-like structure, with string ids for tokenizer used and parameters
        #     passed and dictionaries mapping doc id to list of tokens
        self.tokenized_corpora = None
        # should be a dictionary-like structure, with string ids for vectorizer used and parameters
        #     passed and dictionaries mapping doc id to list of tokens
        self.vectorized_corpora = None
        # should be a dictionary-like structure, with string ids for model used and parameters passed
        #     and dictionaries mapping doc id to list of tokens
        self.modeled_corpora = None

    def save(self, filename, saved_data=None):
        """Persist this object to disk somehow.

        You can save your data in any number of files in any format, but at a minimum, you need one json file that
        describes enough to bootstrap the loading process.  Namely, you must have a key called 'class' so that upon
        loading the output, the correct class can be instantiated and used to load any other data.  You don't have
        to implement anything for saved_data, but it is stored as a key next to 'class'.

        """
        with open(filename, "w") as f:
            f.write(jsonpickle.encode({"class": self.__class__.__name__, "saved_data": saved_data}, f))

    def synchronize(self, max_wait, field):
        """By default, operations are synchronous and no additional wait is
        necessary.  Data sources that are asynchronous (ElasticSearch) may
        use this function to wait for "eventual consistency" """
        pass

    @abstractmethod
    def get_filtered_data(self, field_to_get, filter=""):
        raise NotImplementedError

    def close(self):
        pass


def load_output(filename):
    with open(filename) as f:
        output_details = jsonpickle.decode(f.read())
    return registered_outputs[output_details['class']](**output_details["saved_data"])
