from __future__ import absolute_import

import gensim

from .model_base import TopicModelBase

# Doctest imports
from topik.preprocessing import preprocess
from topik.readers import read_input
from topik.tests import test_data_path


class LDA(TopicModelBase):
    """A high interface for an LDA (Latent Dirichlet Allocation) model.

    Parameters
    ----------
    corpus_input: CorpusBase-derived object
        object fulfilling basic Corpus interface (preprocessed, tokenized text).
        see topik.intermediaries.tokenized_corpus for more info.

    >>> raw_data = read_input(
            '{}/test-data-1.json', "text")
    >>> processed_data = preprocess(raw_data)  # preprocess returns a DigestedDocumentCollection
    >>> model = LDA(processed_data, ntopics=3)
 
    """.format(test_data_path)
    def __init__(self, corpus_input, ntopics=10, **kwargs):
        self.model = gensim.models.LdaModel(corpus_input, num_topics=ntopics,
                                            id2word=corpus_input.get_id2word_dict(), **kwargs)

    def save(self, filename):
        self.model.save(filename)

    def get_top_words(self, topn):
        top_words = [self.model.show_topic(topicno, topn) for topicno in range(self.model.num_topics)]
        return top_words
