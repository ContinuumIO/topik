import nose.tools as nt

from topik.fileio import json_stream, large_json
from topik.tests import test_data_path
from ._solutions import solution_json_stream, solution_large_json

def test_read_document_json_stream():
    loaded_corpus = json_stream('{}/test_data_json_stream.json'.format(
                               test_data_path))
    nt.assert_true(solution_json_stream == next(iter(loaded_corpus))['abstract'])

def test_read_large_json():
    loaded_corpus = large_json('{}/test_data_large_json.json'.format(test_data_path),
                               json_prefix='item._source.isAuthorOf')
    nt.assert_true(solution_large_json == next(iter(loaded_corpus))['text'])

# TODO: add output test(s)