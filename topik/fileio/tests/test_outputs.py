import os
import time
import unittest

import elasticsearch

from topik.fileio.base_output import load_output
from topik.fileio.reader import read_input
from topik.fileio.tests import test_data_path
from topik.fileio.out_elastic import ElasticSearchOutput

#test_data_path = os.path.join(test_data_path, "test_data_json_stream.json")

INDEX = "topik_unittest"
SAVE_FILENAME = "test_save"

class BaseOutputTest(object):
    test_raw_data = None

    def test_year_filtering(self):
        result_list = list(self.test_raw_data.get_date_filtered_data(start=1975,
                                                                     end=1999,
                                                                     filter_field="year"))
        self.assertEqual(len(result_list), 25)
        self.assertTrue(-1611117933394825767 in [int(item[0]) for item in
                        result_list])

    def test_generator_without_id(self):
        data = list(self.test_raw_data.get_generator_without_id())
        self.assertEqual(len(data), 100)
        self.assertFalse(data[0] == data[1])

    def test_save_file(self):
        self.test_raw_data.save(SAVE_FILENAME)
        self.assertTrue(os.path.exists(SAVE_FILENAME))

    def test_load_file(self):
        self.test_raw_data.save(SAVE_FILENAME)
        # TODO: should this be self.test_raw_data
        test_raw_data = load_output(SAVE_FILENAME)
        self.assertEqual(len(test_raw_data), 100)

    def test_has_filter_string(self):
        self.assertEqual(self.test_raw_data.filter_string, "")
        date_data = self.test_raw_data.get_date_filtered_data(1970, 2000)
        self.assertNotEqual(date_data.filter_string, "")


class TestInMemoryOutput(unittest.TestCase, BaseOutputTest):
    def setUp(self):
        self.output_type = "InMemoryOutput"
        self.output_args = {}
        self.test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")


class TestElasticSearchOutput(unittest.TestCase, BaseOutputTest):
    def setUp(self):
        self.test_raw_data = ElasticSearchOutput(
            source='localhost',
            index=INDEX,
            content_field='abstract'
        )

        '''
        self.test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",
            output_type=ElasticSearchOutput.class_key(),
            output_args={'source': 'localhost',
                         'index': INDEX},
            synchronous_wait=30)
        '''

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        instance.indices.delete(INDEX)
        if instance.indices.exists("{}_year_alias_date".format(INDEX)):
            instance.indices.delete("{}_year_alias_date".format(INDEX))
        time.sleep(1)
        # TODO: delete the file from disk