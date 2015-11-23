import os

from topik.simple_run.run import run_model
from topik.fileio.tests import test_data_path


def test_run():
    run_model(os.path.join(test_data_path, "test_data_json_stream.json"), content_field="abstract")
    assert os.path.isfile("termite.html")
    os.remove("termite.html")
