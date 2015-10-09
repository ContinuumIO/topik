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

    def _get_term_data(self):
        term_doc_count_df = pd.DataFrame.from_records([{'tokenid': tokenid, 'token': token,
                                           'doc_count': self._corpus._dict.dfs.get(tokenid, 0)}
                    for tokenid, token in self._corpus._dict.id2token.items()], index="tokenid")

        term_topic_df = pd.DataFrame([
                pd.DataFrame.from_records(self._model.show_topic(topic_no, None),
                                         columns=['topic' + str(topic_no) + 'dist', 'token'],
                                         index='token')['topic' + str(topic_no) + 'dist']
                for topic_no in range(self._model.num_topics)]).T

        token2id_df = pd.DataFrame(self._corpus._dict.token2id.items())
        token2id_df = token2id_df.set_index(0)
        term_topic_df = pd.concat([term_topic_df, token2id_df], axis=1)
        term_topic_df = term_topic_df.set_index(1)

        term_data_df = pd.concat([term_doc_count_df, term_topic_df], axis=1)
        term_data_df.index.name = 'token_id'
        return term_data_df

    def _get_vocab(self):
        return self._corpus._dict.values()

    def _get_term_frequency(self):
        self._corpus._dict.save_as_text(os.path.join(test_data_path, 'dictionary'),
                                      sort_by_word=False)
        # TODO: see gensim source to see how it's saving this to file, then use that

        df = pd.read_csv(os.path.join(test_data_path, 'dictionary'), sep='\t',
                         index_col=0, header=None)
        df = df.sort_index()
        return df[2]

    def _get_topic_term_dists(self):
        term_topic_df = pd.DataFrame()
        for topic_no in range(self._model.num_topics):
            topic_df = pd.DataFrame(self._model.show_topic(topic_no, None))
            topic_df = topic_df.set_index(1)
            topic_df.columns = ['topic' + str(topic_no)]
            term_topic_df = pd.concat([term_topic_df, topic_df], axis=1)
        term_topic_df = term_topic_df.T
        term_topic_df.columns.name = 'terms'
        term_topic_df.index.name = 'topics'
        return term_topic_df

    def _get_doc_data(self):
        doc_data_df = self._get_doc_topic_dists()
        doc_data_df['doc_length'] = self._get_doc_lengths()
        return doc_data_df

    def _get_doc_topic_dists(self):
        id_index, bow_corpus = zip(*[(id, self._corpus._dict.doc2bow(doc_tokens))
                              for id, doc_tokens in self._corpus._corpus])

        doc_topic_dists = list(self._model[bow_corpus])

        for i, doc in enumerate(doc_topic_dists):
            for j, topic in enumerate(doc):
                doc_topic_dists[i][j] = doc_topic_dists[i][j][1]

        doc_topic_dists_df = pd.DataFrame(doc_topic_dists, index=id_index)
        doc_topic_dists_df.columns = ['topic'+str(i)+'dist' for i in range(
                                                doc_topic_dists_df.shape[1])]
        return doc_topic_dists_df

    def _get_doc_lengths(self):
        id_index, doc_lengths = zip(*[(id, len(doc)) for id, doc in list(
                                                        self._corpus._corpus)])
        return pd.Series(doc_lengths, index=id_index)
