"""This file handles the storage of data from loading and analysis.

More accurately, the files written and read from this file describe how to read/write actual data, such that the
actual format of any data need not be tightly defined.
"""

import json


class Persistor(object):
    _storage = {"corpus": None, "models": {}}

    def __init__(self, filename=None):
        if filename:
            self.load_data(filename)

    def store_corpus(self, data_dict):
        self._storage["corpus"] = data_dict

    def store_model(self, model_id, model_dict):
        self._storage["models"][model_id] = model_dict

    def get_corpus_dict(self):
        return self._storage["corpus"]

    def get_model_details(self, model_id):
        return self._storage["models"].get(model_id, None)

    def list_available_models(self):
        return self._storage["models"].keys()

    def persist_data(self, filename):
        with open(filename, "w") as f:
            json.dump(self._storage, f)

    def load_data(self, filename):
        with open(filename, "r") as f:
            self._storage = json.load(f)
