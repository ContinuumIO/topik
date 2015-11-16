# -*- coding: utf-8 -*-

import itertools
import logging
import math

import numpy as np
import pandas as pd

from .base_model_output import TopicModelResultBase
from ._registry import register


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


# def _rand_mat(sizex, sizey):
#     ret = []
#     for i in xrange(sizex):
#         ret.append([])
#         for _ in xrange(sizey):
#             ret[-1].append(random.random())
#         norm = sum(ret[-1])
#         for j in xrange(sizey):
#             ret[-1][j] /= norm
#     return ret

def _rand_mat(cols, rows):
    out = np.random.random((rows, cols))
    for row in out:
        row /= row.sum()
    return out


def _cal_p_dw(vectorized_data, topic_array, zw, dz, beta, p_dw):
    for d, (doc_id, doc) in enumerate(vectorized_data):
        for word_id, word_ct in doc.items():
            tmp = 0
            for _ in range(word_ct):
                for z in topic_array:
                    tmp += (zw[z][word_id]*dz[d][z])**beta
            p_dw[-1][word_id] = tmp
    return p_dw


def _e_step(vectorized_data, dw_z, topic_array, zw, dz, beta, p_dw):
    for d, (doc_id, doc) in enumerate(vectorized_data):
        for word_id, word_ct in doc.items():
            dw_z[-1][word_id] = []
            for z in topic_array:
                dw_z[-1][word_id].append(((zw[z][word_id]*dz[d][z])**beta)/p_dw[d][word_id])
    return dw_z


def _m_step(vectorized_data, topic_array, unique_word_count, zw, dw_z, dz, each):
    iterators = itertools.tee(vectorized_data, len(topic_array))
    for z in topic_array:
        zw[z] = 0
        for d, (doc_id, doc) in enumerate(iterators[z]):
            for word_id, word_ct in doc.items():
                zw[z][word_id] += word_ct*dw_z[d][word_id][z]
        # normalize by sum of topic word weights
        zw[z] /= sum(zw[z])
    for d, (doc_id, doc) in enumerate(vectorized_data):
        dz[d] = 0
        for z in topic_array:
            for word_id, word_ct in doc.items():
                dz[d][z] += word_ct * dw_z[d][word_id][z]
        for z in topic_array:
            dz[d][z] /= each[d]
    return zw, dz


def _cal_likelihood(vectorized_data, p_dw):
    likelihood = 0
    for d, (doc_id, doc) in enumerate(vectorized_data):
        for word_id, word_ct in doc.items():
            likelihood += word_ct*math.log(p_dw[d][word_id])
    return likelihood


@register
def PLSA(vectorized_data, ntopics=2, max_iter=100):
    cur = 0
    topic_array = np.arange(ntopics, dtype=np.int32)
    # topic-word matrix
    zw = _rand_mat(vectorized_data.global_term_count, ntopics)
    # total number of identified words for each given document (document length normalization factor?)
    word_count_per_doc = vectorized_data.document_term_counts
    # document-topic matrix
    dz = _rand_mat(ntopics, len(vectorized_data))
    dw_z = [{}, ] * len(vectorized_data)
    p_dw = [{}, ] * len(vectorized_data)
    beta = 0.8
    for i in range(max_iter):
        iter1, iter2, iter3, iter4 = itertools.tee(vectorized_data, 4)
        logging.info('%d iter' % i)
        p_dw = _cal_p_dw(iter1, topic_array, zw, dz, beta, p_dw)
        dw_z = _e_step(iter2, dw_z, topic_array, zw, dz, beta, p_dw)
        zw, dz = _m_step(iter3, topic_array, vectorized_data.global_term_count, zw, dw_z, dz, word_count_per_doc)
        likelihood = _cal_likelihood(iter4, p_dw)
        logging.info('likelihood %f ' % likelihood)
        if cur != 0 and abs((likelihood-cur)/cur) < 1e-8:
            break
        cur = likelihood

    term_topic_df = pd.DataFrame(zw,
                        index=['topic'+str(t)+'dist' for t in range(ntopics)]).T

    term_topic_df.index.name = 'term_id'

    doc_topic_df = pd.DataFrame(dz,
                        index=[doc[0] for doc in vectorized_data],
                        columns=['topic'+str(t)+'dist' for t in range(ntopics)])

    doc_topic_df.index.name = 'doc_id'

    return TopicModelResultBase(doc_topic_matrix=doc_topic_df,
                                topic_term_matrix=term_topic_df)

