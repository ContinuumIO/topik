import nose.tools as nt
import os

from topik.visualizers.pyldavis import _to_py_lda_vis, lda_vis
from topik.models.tests.test_data import test_model_output

def test__to_py_lda_vis():
    model_vis_data = _to_py_lda_vis(test_model_output)
    nt.assert_equal(model_vis_data['vocab'][4], 'airplane')
    nt.assert_equal(model_vis_data['term_frequency'][3], 10)
    nt.assert_almost_equal(model_vis_data['topic_term_dists'][2]['topic1'], 0.169)
    nt.assert_almost_equal(sum(model_vis_data['topic_term_dists'].iloc[1,:]), 1)
    nt.assert_almost_equal(model_vis_data['doc_topic_dists'][1]['doc3'], 0.10)
    nt.assert_almost_equal(sum(model_vis_data['doc_topic_dists'].iloc[2,:]), 1)
    nt.assert_equal(model_vis_data['doc_lengths']['doc4'], 4)


def test_ldavis():
    TEST_FILENAME = 'test_ldavis_output_file'
    lda_vis(test_model_output, mode='save_html', filename=TEST_FILENAME)
    nt.assert_true(os.path.exists(TEST_FILENAME))
    os.remove(TEST_FILENAME)
