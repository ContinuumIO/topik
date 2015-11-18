# -*- coding: utf-8 -*-

import itertools
import logging
import math
import random

from .base_model_output import TopicModelResultBase
from ._registry import register


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def _rand_mat(sizex, sizey):
    ret = []
    for i in xrange(sizex):
        ret.append([])
        for _ in xrange(sizey):
            ret[-1].append(random.random())
        norm = sum(ret[-1])
        for j in xrange(sizey):
            ret[-1][j] /= norm
    return ret


def _cal_p_dw(vectorized_corpus, topic_array, zw, dz, beta, p_dw):
    for d, (doc_id, doc) in enumerate(vectorized_corpus):
        for word_id, word_ct in doc.items():
            tmp = 0
            for _ in range(word_ct):
                for z in topic_array:
                    tmp += (zw[z][word_id]*dz[d][z])**beta
            p_dw[-1][word_id] = tmp
    return p_dw


def _e_step(vectorized_corpus, dw_z, topic_array, zw, dz, beta, p_dw):
    for d, (doc_id, doc) in enumerate(vectorized_corpus):
        for word_id, word_ct in doc.items():
            dw_z[-1][word_id] = []
            for z in topic_array:
                dw_z[-1][word_id].append(((zw[z][word_id]*dz[d][z])**beta)/p_dw[d][word_id])
    return dw_z


def _m_step(vectorized_corpus, topic_array, unique_word_count, zw, dw_z, dz, each):
    iterators = itertools.tee(vectorized_corpus, len(topic_array))
    for z in topic_array:
        zw[z] = [0, ] * unique_word_count
        for d, (doc_id, doc) in enumerate(iterators[z]):
            for word_id, word_ct in doc.items():
                zw[z][word_id] += word_ct*dw_z[d][word_id][z]
    # normalize by sum of topic word weights
    for topic in zw:
        total = sum(topic)
        for term in topic:
            term /= total
    for d, (doc_id, doc) in enumerate(vectorized_corpus):
        dz[d] = [0, ] * len(topic_array)
        for z in topic_array:
            for word_id, word_ct in doc.items():
                dz[d][z] += word_ct * dw_z[d][word_id][z]
        for z in topic_array:
            dz[d][z] /= each[d]
    return zw, dz


def _cal_likelihood(vectorized_corpus, p_dw):
    likelihood = 0
    for d, (doc_id, doc) in enumerate(vectorized_corpus):
        for word_id, word_ct in doc.items():
            likelihood += word_ct*math.log(p_dw[d][word_id])
    return likelihood


@register
def PLSA(vectorized_corpus, ntopics=2, max_iter=100):
    cur = 0
    topic_array = range(ntopics)
    # topic-word matrix
    zw = _rand_mat(ntopics, vectorized_corpus.global_term_count)
    # total number of identified words for each given document (document length normalization factor?)
    word_count_per_doc = vectorized_corpus.document_term_counts
    # document-topic matrix
    dz = _rand_mat(len(vectorized_corpus), ntopics)
    dw_z = [{}, ] * len(vectorized_corpus)
    p_dw = [{}, ] * len(vectorized_corpus)
    beta = 0.8
    for i in range(max_iter):
        iter1, iter2, iter3, iter4 = itertools.tee(vectorized_corpus, 4)
        logging.info('%d iter' % i)
        p_dw = _cal_p_dw(iter1, topic_array, zw, dz, beta, p_dw)
        dw_z = _e_step(iter2, dw_z, topic_array, zw, dz, beta, p_dw)
        zw, dz = _m_step(iter3, topic_array, vectorized_corpus.global_term_count, zw, dw_z, dz, word_count_per_doc)
        likelihood = _cal_likelihood(iter4, p_dw)
        logging.info('likelihood %f ' % likelihood)
        if cur != 0 and abs((likelihood-cur)/cur) < 1e-8:
            break
        cur = likelihood

    return TopicModelResultBase(doc_topic_matrix=dz,
                                topic_term_matrix=zw)

