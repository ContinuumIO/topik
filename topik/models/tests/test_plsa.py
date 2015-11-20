import random

import nose.tools as nt

from topik.models import registered_models, PLSA
from .test_data import test_vectorized_output

from topik.models.plsa import _rand_mat, _e_step, _m_step, _cal_likelihood, _cal_p_dw

ntopics = 2


def test_rand_mat():
    # ntopics, nwords
    rand_mat = _rand_mat(2, 5)
    nt.assert_equal(len(rand_mat), 2)
    for topic in rand_mat:
        nt.assert_equal(len(topic), 5)
        nt.assert_almost_equal(sum(topic), 1)

def test_e_step():
    dz = _rand_mat(len(test_vectorized_output), ntopics)
    dw_z = [{}, ] * len(test_vectorized_output)
    p_dw = [{}, ] * len(test_vectorized_output)
    zw = _rand_mat(ntopics, test_vectorized_output.global_term_count)
    dw_z = _e_step(test_vectorized_output, dw_z, range(ntopics), zw, dz, 0.8, p_dw)
    nt.assert_almost_equal(dw_z, 1)

def test_m_step():
    dz = _rand_mat(len(test_vectorized_output), ntopics)
    dw_z = [{}, ] * len(test_vectorized_output)
    zw = _rand_mat(ntopics, test_vectorized_output.global_term_count)
    zw, dz = _m_step(test_vectorized_output, range(ntopics), zw, dw_z, dz)
    for topic in zw:
        nt.assert_almost_equal(sum(topic), 1)
    for doc in dz:
        nt.assert_almost_equal(sum(doc), 1)
    raise NotImplementedError

def test_cal_likelihood():
    raise NotImplementedError

def test_cal_p_dw():
    raise NotImplementedError

def test_train():
    random.seed(42)
    model_output = PLSA(test_vectorized_output, ntopics=2)
    for doc in model_output.doc_topic_matrix:
        nt.assert_almost_equal(sum(doc), 1)
    for topic in model_output.topic_term_matrix:
        nt.assert_almost_equal(sum(topic), 1)


def test_registration():
    nt.assert_true("PLSA" in registered_models)
