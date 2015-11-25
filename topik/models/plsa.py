# -*- coding: utf-8 -*-

import logging

import numpy as np

from .base_model_output import ModelOutput
from ._registry import register

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.WARNING)


def _rand_mat(rows, cols):
    out = np.random.random((rows, cols))
    for row in out:
        row /= row.sum()
    return out


def _cal_p_dw(words_in_docs, word_cts_in_docs, topic_array, zw, dz, beta, p_dw):
    for (d, doc_id, words) in words_in_docs:
        p_dw[d, words] = (word_cts_in_docs[doc_id] * (zw[:, words]*np.expand_dims(dz[d, :], 1))**beta).sum(axis=0)
    return p_dw


def _e_step(words_in_docs, dw_z, topic_array, zw, dz, beta, p_dw):
    for (d, _, words) in words_in_docs:
        dw_z[d, words, :] = ((zw[:, words].T * dz[d, :]) ** beta) / np.expand_dims(p_dw[d, words], 1)
    return dw_z


def _m_step(words_in_docs, word_cts_in_docs, topic_array, zw, dw_z, dz):
    zw[:] = 0
    for (d, doc_id, words) in words_in_docs:
        zw[:, words] += word_cts_in_docs[doc_id]*dw_z[d, words].T
    # normalize by sum of topic word weights
    zw /= np.expand_dims(zw.sum(axis=1), 1)
    for (d, doc_id, words) in words_in_docs:
        dz[d] = (word_cts_in_docs[doc_id] * dw_z[d, words].T).sum(axis=1)
    dz /= np.expand_dims(dz.sum(axis=1), 1)
    return zw, dz


def _cal_likelihood(words_in_docs, word_cts_in_docs, p_dw):
    likelihood = 0
    for (d, doc_id, words) in words_in_docs:
        likelihood += sum(word_cts_in_docs[doc_id] * np.log(p_dw[d][words]))
    return likelihood


def _get_topic_term_matrix(zw, ntopics, id_term_map):
    labeled_zw = {"topic"+str(topicno): zw[topicno].tolist() for topicno in range(ntopics)}
    return labeled_zw


def _get_doc_topic_matrix(dz, ntopics, vectorized_corpus):
    labeled_dz = {doc_id: dz[i].tolist() for i, (doc_id, vector) in enumerate(vectorized_corpus.get_vectors())}
    return labeled_dz


def _PLSA(vectorized_corpus, ntopics, max_iter):
    cur = 0
    topic_array = np.arange(ntopics, dtype=np.int32)
    # topic-word matrix
    zw = _rand_mat(ntopics, vectorized_corpus.global_term_count)
    # document-topic matrix
    dz = _rand_mat(len(vectorized_corpus), ntopics)
    dw_z = np.zeros((len(vectorized_corpus), vectorized_corpus.global_term_count, ntopics))
    p_dw = np.zeros((len(vectorized_corpus), vectorized_corpus.global_term_count))
    beta = 0.8
    words_in_docs = [(id, doc_id, [word_id for word_id, _ in doc.items()])
                     for id, (doc_id, doc) in enumerate(vectorized_corpus.get_vectors())]
    word_cts_in_docs = {doc_id: [ct for _, ct in doc.items()] for doc_id, doc in vectorized_corpus.get_vectors()}
    for i in range(max_iter):
        p_dw = _cal_p_dw(words_in_docs, word_cts_in_docs, topic_array, zw, dz, beta, p_dw)
        dw_z = _e_step(words_in_docs, dw_z, topic_array, zw, dz, beta, p_dw)
        zw, dz = _m_step(words_in_docs, word_cts_in_docs, topic_array, zw, dw_z, dz)
        likelihood = _cal_likelihood(words_in_docs, word_cts_in_docs, p_dw)
        if cur != 0 and abs((likelihood-cur)/cur) < 1e-8:
            break
        cur = likelihood
    topic_term_matrix = _get_topic_term_matrix(zw, ntopics, vectorized_corpus.id_term_map)
    doc_topic_matrix = _get_doc_topic_matrix(dz, ntopics, vectorized_corpus)
    return topic_term_matrix, doc_topic_matrix

@register
def plsa(vectorized_corpus, ntopics, max_iter=100, **kwargs):
    return ModelOutput(vectorized_corpus=vectorized_corpus, model_func=_PLSA, ntopics=ntopics, max_iter=max_iter, **kwargs)


