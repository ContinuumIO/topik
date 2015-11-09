import nose.tools as nt

from topik.fileio.in_json import read_json_stream, read_large_json, __is_iterable
from topik.fileio.tests import test_data_path
from ._solutions import solution_json_stream, solution_large_json

def test_read_document_json_stream():
    documents = read_json_stream('{}/test_data_json_stream.json'.format(
                               test_data_path))
    nt.assert_true(solution_json_stream == next(documents)['abstract'])

def test___is_iterable():
    #iterables
    nt.assert_true(__is_iterable([1,2,3]))
    nt.assert_true(__is_iterable('abc'))
    nt.assert_true(__is_iterable({'a': 1, 'b': 2}))
    nt.assert_true(__is_iterable((1,2,3)))
    nt.assert_true(__is_iterable({1,2,3}))
    #non-iterables
    nt.assert_false(__is_iterable(123))
    nt.assert_false(__is_iterable(12.3))



def test_read_large_json():
    documents = read_large_json('{}/test_data_large_json.json'.format(test_data_path),
                               json_prefix='item._source.isAuthorOf')
    nt.assert_true(solution_large_json == next(documents)['text'])
