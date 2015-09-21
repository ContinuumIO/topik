from __future__ import absolute_import

import gensim

from topik.intermediaries.digested_document_collection import DigestedDocumentCollection
from .model_base import TopicModelBase, register_model

# Doctest imports
from topik.preprocessing import preprocess
from topik.readers import read_input
from topik.tests import test_data_path


@register_model
class LDA(TopicModelBase):
    """A high interface for an LDA (Latent Dirichlet Allocation) model.

    Parameters
    ----------
    corpus_input: CorpusBase-derived object
        object fulfilling basic Corpus interface (preprocessed, tokenized text).
        see topik.intermediaries.tokenized_corpus for more info.

    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
    >>> processed_data = preprocess(raw_data)  # preprocess returns a DigestedDocumentCollection
    >>> model = LDA(processed_data, ntopics=3)
 
    """
    def __init__(self, corpus_input=None, ntopics=10, load_filename=None, **kwargs):
        if corpus_input is not None:
            self.model = gensim.models.LdaModel(list(iter(corpus_input)), num_topics=ntopics,
                                                id2word=corpus_input.get_id2word_dict(), **kwargs)
            self.corpus = corpus_input
        elif load_filename is not None:
            self.model = gensim.models.LdaModel.load(load_filename)
            self.corpus = DigestedDocumentCollection.load(load_filename)

    def save(self, filename):
        self.model.save(filename)
        saved_data = {"class": "LDA", "load_filename": filename}
        return super(LDA, self).save(filename, saved_data)

    def get_top_words(self, topn):
        top_words = [self.model.show_topic(topicno, topn) for topicno in range(self.model.num_topics)]
        return top_words
