from topik.readers import read_input
from topik.tests import test_data_path
from topik.intermediaries.raw_data import load_persisted_corpus
from topik.preprocessing import preprocess
from topik.models import registered_models

INDEX = "topik_time_raw_corpus"


class TimeSuite:
    params = ([key for key in registered_models], [10, 30, 50])
    """
    # TODO: This presently doesn't work with ASV.
    def setup_cache(self):
        raw_data_dict = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        processed_data = preprocess(raw_data_dict)
        processed_data.save(INDEX)
    """

    def setup(self, model, ntopics):
        # self.raw_data_dict = load_persisted_corpus(INDEX)
        self.raw_data_dict = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        self.processed_data = preprocess(self.raw_data_dict)
        self.model = registered_models[model](self.processed_data, ntopics)

    def time_preprocess_simple_tokenize(self):
        preprocess(self.raw_data_dict)

    def time_train_model(self, model, ntopics):
        self.model.train()


class MemSuite:
    """
    # TODO: This presently doesn't work with ASV.
    def setup_cache(self):
        raw_data_dict = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        processed_data = preprocess(raw_data_dict)
        processed_data.save(INDEX)
    """

    def setup(self):
        # self.raw_data_dict = load_persisted_corpus(INDEX)
        self.raw_data_dict = read_input('{}/test_data_json_stream.json'.format(
            test_data_path), content_field="abstract")
        self.processed_data = preprocess(self.raw_data_dict)

    def mem_preprocess_simple_tokenize(self):
        preprocess(self.raw_data_dict)


