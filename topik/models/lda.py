from __future__ import absolute_import

import gensim

from .model_base import TopicModelBase


class LDA(TopicModelBase):
    """A high interface for an LDA (Latent Dirichlet Allocation) model.

    Parameters
    ----------
    corpus_input: CorpusBase-derived object
        object fulfilling basic Corpus interface (preprocessed, tokenized text).
        see topik.intermediaries.tokenized_corpus for more info.

    >>> my_lda = LDA(corpus_input, ntopics=10)

    """
    def __init__(self, corpus_input, ntopics=10, **kwargs):
        self.model = gensim.models.LdaModel(corpus_input, num_topics=ntopics,
                                            id2word=corpus_input.get_id2word_dict(), **kwargs)

    def save(self, filename):
        self.model.save(filename)

    def get_top_words(self, topn):
        top_words = [self.model.show_topic(topicno, topn) for topicno in range(self.model.num_topics)]
        return top_words
