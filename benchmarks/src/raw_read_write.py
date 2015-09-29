from topik.readers import read_input
from topik.tests import test_data_path
from topik.intermediaries.raw_data import load_persisted_corpus, ElasticSearchCorpus

INDEX = "topik_time_raw_corpus"
INDEX_2 = "topik_time_raw_corpus_2"

class TimeSuite:
    def setup(self):
        self.raw_data_dict = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        self.raw_data_ES = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",

            output_type=ElasticSearchCorpus.class_key(),
            output_args= {'host': 'localhost',
                          'index': INDEX},
            synchronous_wait=30)
        self.raw_data_dict.save("test_raw_corpus_dict")
        self.raw_data_ES.save("test_raw_corpus_es")

    def teardown(self):
        import glob
        import os
        import elasticsearch
        for f in glob.glob("test_raw_*"):
            os.remove(f)
        instance = elasticsearch.Elasticsearch("localhost")
        for index in (INDEX, INDEX_2):
            if instance.indices.exists(index):
                instance.indices.delete(index)


    def time_read_into_dict(self):
        raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")

    def time_read_into_ES(self):
        raw_data_ES = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",
            output_type=ElasticSearchCorpus.class_key(),
            output_args= {'host': 'localhost',
                          'index': INDEX_2},
            synchronous_wait=30)

    def time_save_dict(self):
        self.raw_data_dict.save("test_raw_corpus_dict")

    def time_load_dict(self):
        load_persisted_corpus("test_raw_corpus_dict")

    def time_save_ES(self):
        self.raw_data_ES.save("test_raw_corpus_es")

    def time_load_ES(self):
        load_persisted_corpus("test_raw_corpus_es")


class MemSuite:
    def setup(self):
        self.raw_data = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        self.raw_data_ES = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",
            output_type=ElasticSearchCorpus.class_key(),
            output_args= {'host': 'localhost',
                          'index': INDEX},
            synchronous_wait=30)

    def teardown(self):
        import glob
        import os
        import elasticsearch
        for f in glob.glob("test_raw_*"):
            os.remove(f)
        instance = elasticsearch.Elasticsearch("localhost")
        for index in (INDEX, INDEX_2):
            if instance.indices.exists(index):
                instance.indices.delete(index)

    def mem_read_into_dict(self):
        return read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")

    def mem_read_into_ES(self):
        return read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract",
            output_type=ElasticSearchCorpus.class_key(),
            output_args= {'host': 'localhost',
                          'index': INDEX_2},
            synchronous_wait=30)

