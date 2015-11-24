import random

import nose.tools as nt
import numpy as np

from topik.models import registered_models
from topik.models.tests.test_data import test_vectorized_output

from topik.models.plsa import _rand_mat, _e_step, _m_step, _cal_likelihood, _cal_p_dw, plsa

ntopics = 2
words_in_docs = [(id, doc_id, [word_id for word_id, _ in doc.items()])
                     for id, (doc_id, doc) in enumerate(test_vectorized_output.get_vectors())]
word_cts_in_docs = {doc_id: [ct for _, ct in doc.items()] for doc_id, doc in test_vectorized_output.get_vectors()}

def test_rand_mat():
    # ntopics, nwords
    rand_mat = _rand_mat(2, 5)
    nt.assert_equal(len(rand_mat), 2)
    for topic in rand_mat:
        nt.assert_equal(len(topic), 5)
        nt.assert_almost_equal(sum(topic), 1)


def test_em():
    dz = _rand_mat(len(test_vectorized_output), ntopics)
    dw_z = np.zeros((len(test_vectorized_output), test_vectorized_output.global_term_count, ntopics))
    p_dw = np.zeros((len(test_vectorized_output), test_vectorized_output.global_term_count))
    zw = _rand_mat(ntopics, test_vectorized_output.global_term_count)
    p_dw = _cal_p_dw(words_in_docs, word_cts_in_docs, range(ntopics), zw, dz, 0.8, p_dw)
    dw_z = _e_step(words_in_docs, dw_z, range(ntopics), zw, dz, 0.8, p_dw)
    zw, dz = _m_step(words_in_docs, word_cts_in_docs, range(ntopics), zw, dw_z, dz)
    for topic in zw:
        nt.assert_almost_equal(sum(topic), 1)
    for doc in dz:
        nt.assert_almost_equal(sum(doc), 1)


def test_cal_likelihood():
    dz = _rand_mat(len(test_vectorized_output), ntopics)
    zw = _rand_mat(ntopics, test_vectorized_output.global_term_count)
    p_dw = np.zeros((len(test_vectorized_output), test_vectorized_output.global_term_count))
    p_dw = _cal_p_dw(words_in_docs, word_cts_in_docs, range(ntopics), zw, dz, 0.8, p_dw)
    likelihood = _cal_likelihood(words_in_docs, word_cts_in_docs, p_dw)
    nt.assert_less(likelihood, 0)


def test_train():
    random.seed(42)
    model_output = plsa(test_vectorized_output, ntopics=2)
    for doc in model_output.doc_topic_matrix.values():
        nt.assert_almost_equal(sum(doc), 1)
    for topic in model_output.topic_term_matrix.values():
        nt.assert_almost_equal(sum(topic), 1)


def test_registration():
    nt.assert_true("plsa" in registered_models)

if __name__ == "__main__":
    test_train()