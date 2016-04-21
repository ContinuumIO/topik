import os
import unittest
import logging
import elasticsearch

from topik.fileio.base_output import load_output
from topik.fileio.reader import read_input
from topik.fileio.tests import test_data_path
from topik.fileio.out_elastic import ElasticSearchOutput
from topik.fileio.out_memory import InMemoryOutput
from elasticsearch.exceptions import ConnectionError
from nose.plugins.skip import SkipTest

INDEX = "topik_unittest"
SAVE_FILENAME = "test_save.topikdata"
CONTENT_FIELD = "abstract"

# make logging quiet during testing, to keep Travis CI logs short.

logging.basicConfig()
logging.getLogger('elasticsearch').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)


class BaseOutputTest(object):
    test_raw_data = None

    def test_get_filtered_data(self):
        data = list(self.test_raw_data.get_filtered_data(CONTENT_FIELD))
        self.assertEqual(len(data), 100)
        self.assertFalse(data[0] == data[1])

    def test_save_file(self):
        self.test_raw_data.save(SAVE_FILENAME)
        self.assertTrue(os.path.exists(SAVE_FILENAME))
        os.remove(SAVE_FILENAME)

    def test_load_file(self):
        self.test_raw_data.save(SAVE_FILENAME)
        self.test_raw_data = load_output(SAVE_FILENAME)
        data = list(self.test_raw_data.get_filtered_data(CONTENT_FIELD))
        self.assertEqual(len(data), 100)
        os.remove(SAVE_FILENAME)

    def test_get_date_filtered_data(self):
        result_list = list(self.test_raw_data.get_date_filtered_data(field_to_get=CONTENT_FIELD,
                                                                     start=1975,
                                                                     end=1999,
                                                                     filter_field="year"))
        self.assertEqual(len(result_list), 25)
        self.assertTrue(-1611117933394825767 in [int(item[0]) for item in
                        result_list])


class TestInMemoryOutput(unittest.TestCase, BaseOutputTest):
    def setUp(self):
        self.test_raw_data = InMemoryOutput()
        self.test_raw_data.import_from_iterable(read_input(
            '{}/test_data_json_stream.json'.format(test_data_path)),
            field_to_hash=CONTENT_FIELD)


class TestElasticSearchOutput(unittest.TestCase, BaseOutputTest):
    def setUp(self):
        self.test_raw_data = ElasticSearchOutput(
            source='localhost',
            index=INDEX,
            content_field='abstract'
        )
        try:
            self.test_raw_data.import_from_iterable(read_input(
                '{}/test_data_json_stream.json'.format(test_data_path)),
                field_to_hash=CONTENT_FIELD)

        except ConnectionError:
            raise SkipTest("Skipping Elasticsearch test - elasticsearch not running")

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        instance.indices.delete(INDEX)
        if instance.indices.exists("{}_year_alias_date".format(INDEX)):
            instance.indices.delete("{}_year_alias_date".format(INDEX))

