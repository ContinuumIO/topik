import unittest

import elasticsearch

from topik.readers import read_input
from topik.tests import test_data_path

INDEX = "topik_unittest"

class BaseCorpus(object):
    test_raw_data = None

    def test_year_filtering(self):
        result_list = list(self.test_raw_data.get_data_by_year(start_year=1975,
                                                        end_year=1999,
                                                        year_field="year"))

        self.assertEqual(len(result_list), 25)
        self.assertTrue(-1611117933394825767 in [int(item[0]) for item in
                        result_list])

class TestDictionaryCorpus(unittest.TestCase, BaseCorpus):
    def setUp(self):
        self.test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")

class TestElasticSearchCorpus(unittest.TestCase, BaseCorpus):
    def setUp(self):
        self.test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",
            output_type="elasticsearch",
            output_args= {'host': 'localhost',
                          'index': INDEX},
               synchronous_wait=30)

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        instance.indices.delete(INDEX)
        if instance.indices.exists("{}_year_date".format(INDEX)):
            instance.indices.delete("{}_year_date".format(INDEX))
