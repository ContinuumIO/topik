import unittest
import os
import time

import elasticsearch

from topik.readers import read_input
from topik.intermediaries.raw_data import load_persisted_corpus, ElasticSearchCorpus
from topik.tests import test_data_path


INDEX = "topik_unittest"
SAVE_FILENAME = "test_save"

class BaseCorpus(object):
    test_raw_data = None

    def test_year_filtering(self):
        result_list = list(self.test_raw_data.get_date_filtered_data(start=1975,
                                                                     end=1999,
                                                                     field="year"))
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
        test_raw_data = load_persisted_corpus(SAVE_FILENAME)
        self.assertEqual(len(test_raw_data), 100)

    def test_has_filter_string(self):
        self.assertEqual(self.test_raw_data.filter_string, "")
        date_data = self.test_raw_data.get_date_filtered_data(1970, 2000)
        self.assertNotEqual(date_data.filter_string, "")


class TestDictionaryCorpus(unittest.TestCase, BaseCorpus):
    def setUp(self):
        self.test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")


class TestElasticSearchCorpus(unittest.TestCase, BaseCorpus):
    def setUp(self):
        self.test_raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",
            output_type=ElasticSearchCorpus.class_key(),
            output_args={'source': 'localhost',
                         'index': INDEX},
            synchronous_wait=30)

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        instance.indices.delete(INDEX)
        if instance.indices.exists("{}_year_alias_date".format(INDEX)):
            instance.indices.delete("{}_year_alias_date".format(INDEX))
        time.sleep(1)
