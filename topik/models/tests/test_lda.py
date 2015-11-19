import nose.tools as nt

from .test_data import test_vectorized_output
from topik.models.lda import LDA


def test_train():
    model_output = LDA(test_vectorized_output, ntopics=2)
    for doc in model_output.doc_topic_matrix:
        nt.assert_almost_equal(sum(doc), 1)
    for topic in model_output.topic_term_matrix:
        nt.assert_almost_equal(sum(topic), 1)

