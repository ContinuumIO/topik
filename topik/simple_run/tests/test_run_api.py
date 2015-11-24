import os

from topik.simple_run.run import run_pipeline
from topik.fileio.tests import test_data_path


def test_run():
    run_pipeline(os.path.join(test_data_path, "test_data_json_stream.json"), content_field="abstract",
                 termite_plot=True, lda_vis=False)
    assert os.path.isfile("termite.html")
    os.remove("termite.html")
