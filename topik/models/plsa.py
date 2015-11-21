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
    for d, (doc_id, words) in enumerate(words_in_docs.items()):
        for z in topic_array:
            p_dw[d, words] = word_cts_in_docs[doc_id] * (zw[z][words]*dz[d][z])**beta
    return p_dw


def _e_step(words_in_docs, dw_z, topic_array, zw, dz, beta, p_dw):
    for d, words in enumerate(words_in_docs.values()):
        for z in topic_array:
            dw_z[d, words, z] = ((zw[z, words] * dz[d, z]) ** beta) / p_dw[d, words]
    return dw_z


def _m_step(words_in_docs, word_cts_in_docs, topic_array, zw, dw_z, dz):
    for z in topic_array:
        zw[z] = 0
        for d, (doc_id, words) in enumerate(words_in_docs.items()):
            zw[z, words] += word_cts_in_docs[doc_id]*dw_z[d, words, z]
    # normalize by sum of topic word weights
    for topic in zw:
        topic /= sum(topic)
    for d, (doc_id, words) in enumerate(words_in_docs.items()):
        for z in topic_array:
            dz[d, z] = sum(word_cts_in_docs[doc_id] * dw_z[d, words, z])
        dz[d] /= sum(dz[d])
    return zw, dz


def _cal_likelihood(words_in_docs, word_cts_in_docs, p_dw):
    likelihood = 0
    for d, (doc_id, words) in enumerate(words_in_docs.items()):
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
    topic_array = range(ntopics)
    # topic-word matrix
    zw = _rand_mat(ntopics, vectorized_corpus.global_term_count)
    # document-topic matrix
    dz = _rand_mat(len(vectorized_corpus), ntopics)
    dw_z = np.zeros((len(vectorized_corpus), vectorized_corpus.global_term_count, ntopics))
    p_dw = np.zeros((len(vectorized_corpus), vectorized_corpus.global_term_count))
    beta = 0.8
    words_in_docs = {doc_id: [word_id for word_id, _ in doc.items()] for doc_id, doc in vectorized_corpus.get_vectors()}
    word_cts_in_docs = {doc_id: [ct for _, ct in doc.items()] for doc_id, doc in vectorized_corpus.get_vectors()}
    for i in range(max_iter):
        p_dw = _cal_p_dw(words_in_docs, word_cts_in_docs, topic_array, zw, dz, beta, p_dw)
        dw_z = _e_step(words_in_docs, dw_z, topic_array, zw, dz, beta, p_dw)
        zw, dz = _m_step(words_in_docs, word_cts_in_docs, topic_array, zw, dw_z, dz)
        likelihood = _cal_likelihood(words_in_docs, word_cts_in_docs, p_dw)
        if cur != 0 and abs((likelihood-cur)/cur) < 1e-8:
            break
        cur = likelihood
    return _get_topic_term_matrix(zw, ntopics, vectorized_corpus.id_term_map), \
        _get_doc_topic_matrix(dz, ntopics, vectorized_corpus)

@register
def plsa(vectorized_corpus, ntopics, max_iter=100, **kwargs):
    return ModelOutput(vectorized_corpus, _PLSA, ntopics=ntopics, max_iter=max_iter, **kwargs)


