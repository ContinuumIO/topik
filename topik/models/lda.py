from __future__ import absolute_import

import os
import gensim
import pandas as pd

from topik.intermediaries.digested_document_collection import DigestedDocumentCollection
from topik.intermediaries.raw_data import load_persisted_corpus
from .model_base import TopicModelBase, register_model

# Doctest imports
from topik.readers import read_input
from topik.tests import test_data_path


@register_model
class LDA(TopicModelBase):
    """A high-level interface for an LDA (Latent Dirichlet Allocation) model.


    Parameters
    ----------
    corpus_input : CorpusBase-derived object
        object fulfilling basic Corpus interface (preprocessed, tokenized text).
        see topik.intermediaries.tokenized_corpus for more info.
    ntopics : int
        Number of topics to model
    load_filename : None or str
        If not None, this (JSON) file is read to determine parameters of the model persisted to disk.
    binary_filename : None or str
        If not None, this file is loaded by Gensim to bring a disk-persisted model back into memory.


    Attributes
    ----------
    corpus : CorpusBase-derived object, tokenized
    model : Gensim LdaModel instance


    Examples
    --------
    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
    >>> processed_data = raw_data.tokenize()  # preprocess returns a DigestedDocumentCollection
    >>> model = LDA(processed_data, ntopics=3)

    """
    def __init__(self, corpus_input=None, ntopics=10, load_filename=None, binary_filename=None, **kwargs):
        if corpus_input is not None:
            self._model = gensim.models.LdaModel(list(iter(corpus_input)), num_topics=ntopics,
                                                id2word=corpus_input.get_id2word_dict(), **kwargs)
            self._corpus = corpus_input
        elif load_filename is not None and binary_filename is not None:
            self._model = gensim.models.LdaModel.load(binary_filename)
            self._corpus = DigestedDocumentCollection(load_persisted_corpus(load_filename))

    def save(self, filename):
        self._model.save(self.get_model_name_with_parameters())
        saved_data = {"load_filename": filename, "binary_filename": self.get_model_name_with_parameters()}
        return super(LDA, self).save(filename, saved_data)

    def get_top_words(self, topn):
        top_words = [self._model.show_topic(topicno, topn) for topicno in range(self._model.num_topics)]
        return top_words

    def get_model_name_with_parameters(self):
        return "LDA_{}_topics{}".format(self._model.num_topics, self._corpus.filter_string)

    def _get_topic_term_dists(self):
        term_topic_df = pd.DataFrame([
                pd.DataFrame.from_records(self._model.show_topic(topic_no, None),
                                         columns=['topic' + str(topic_no) + 'dist', 'token'],
                                         index='token')['topic' + str(topic_no) + 'dist']
                for topic_no in range(self._model.num_topics)]).T
        term_topic_df['term_id'] = pd.Series(dict(self._corpus._dict.token2id.items()))
        term_topic_df = term_topic_df.set_index('term_id')
        return term_topic_df

    def _get_doc_topic_dists(self):
        id_index, bow_corpus = zip(*[(id, self._corpus._dict.doc2bow(doc_tokens))
                              for id, doc_tokens in self._corpus._corpus])

        doc_topic = list(self._model[bow_corpus])

        for i, doc in enumerate(doc_topic):
            for j, topic in enumerate(doc):
                doc_topic[i][j] = doc_topic[i][j][1]

        doc_topic_df = pd.DataFrame(doc_topic, index=id_index)
        doc_topic_df.columns = ['topic'+str(i)+'dist' for i in range(
                                                doc_topic_df.shape[1])]
        doc_topic_df.index.name = 'doc_id'
        return doc_topic_df
