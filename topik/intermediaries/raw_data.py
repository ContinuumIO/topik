"""
This file is concerned with providing a simple interface for data stored in
Elasticsearch.  The class(es) defined here are fed into the preprocessing step.
"""

import logging
import time
from abc import ABCMeta, abstractmethod
from six import with_metaclass

import json
from elasticsearch import Elasticsearch, helpers


def _get_hash_identifier(input_data, id_field):
    return hash(input_data[id_field])


class CorpusInterface(with_metaclass(ABCMeta)):
    @classmethod
    @abstractmethod
    def class_key(cls):
        """Implement this method to return the string ID with which to store your class."""
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        """This is expected to iterate over your data, returning tuples of (doc_id, <selected field>)"""
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def get_generator_without_id(self, field=None):
        """Returns a generator that yields field content without doc_id associate"""
        raise NotImplementedError

    @abstractmethod
    def append_to_record(self, record_id, field_name, field_value):
        """Used to store preprocessed output alongside input data.

        Field name is destination.  Value is processed value."""
        raise NotImplementedError

    def save(self, filename, saved_data=None):
        """Persist this object to disk somehow.

        You can save your data in any number of files in any format, but at a minimum, you need one json file that
        describes enough to bootstrap the loading prcess.  Namely, you must have a key called 'class' so that upon
        loading the output, the correct class can be instantiated and used to load any other data.  You don't have
        to implement anything for saved_data, but it is stored as a key next to 'class'.

        The base method implementation might be enough for you without extension: give it a try.

        """
        with open(filename+"_CORPUS", "w") as output:
            json.dump({"class": self.__class__.class_key(),
                       "saved_data": saved_data}, output)


class ElasticSearchCorpus(CorpusInterface):
    def __init__(self, host, index, content_field, port=9200, username=None,
                 password=None, doc_type=None, query=None, iterable=None):
        super(ElasticSearchCorpus, self).__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.instance = Elasticsearch(hosts=[{"host": host, "port": port,
                                              "http_auth": "{}:{}".format(username, password)}
                                             ])
        self.index = index
        self.content_field = content_field
        self.doc_type = doc_type
        self.query = query
        if iterable:
            self.import_from_iterable(iterable, content_field)

    @classmethod
    def class_key(cls):
        return "elastic"

    def __iter__(self):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.doc_type)
        for result in results:
            yield result["_id"], result['_source'][self.content_field]

    def __len__(self):
        return self.instance.count(index=self.index, doc_type=self.doc_type)["count"]

    def get_generator_without_id(self, field=None):
        if not field:
            field = self.content_field
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.doc_type)
        for result in results:
            yield result["_source"][field]

    def append_to_record(self, record_id, field_name, field_value):
        self.instance.update(index=self.index, id=record_id, doc_type="continuum",
                             body={"doc": {field_name: field_value}})

    def get_field(self, field=None):
        """Get a different field to iterate over, keeping all other
           connection details."""
        if not field:
            field = self.content_field
        return ElasticSearchCorpus(self.host, self.index, field, self.port,
                                   self.username, self.password, self.doc_type,
                                   self.query)

    def import_from_iterable(self, iterable, id_field="text", batch_size=500):
        """Load data into Elasticsearch from iterable.

        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        id_field: string identifier of field to hash for content ID.  For
            list of dicts, a valid key value in the dictionary is required. For
            list of strings, a dictionary with one key, "text" is created and
            used.
        """
        batch = []
        for item in iterable:
            if isinstance(item, basestring):
                item = {id_field: item}
            id = _get_hash_identifier(item, id_field)
            batch.append({"_id": id, "_source": item, "_type": "continuum"})
            if len(batch) >= batch_size:
                helpers.bulk(client=self.instance, actions=batch, index=self.index)
                batch = []
        if batch:
            helpers.bulk(client=self.instance, actions=batch, index=self.index)

    # TODO: validate input data to ensure that it has valid year data
    def get_data_by_year(self, start_year, end_year, year_field="year"):
        """Queries elasticsearch for all documents within the specified year range
        and returns a generator of the results"""
        index = self.index
        if self.instance.indices.get_field_mapping(field=year_field,
                                           index=index,
                                           doc_type="continuum") != 'date':
            index = self.index+"_{}_date".format(year_field)
            if not self.instance.indices.exists(index) or self.instance.indices.get_field_mapping(field=year_field,
                                           index=index,
                                           doc_type="continuum") != 'date':
                mapping = self.instance.indices.get_mapping(index=self.index,
                                                            doc_type="continuum")
                mapping[self.index]["mappings"]["continuum"]["properties"][year_field] = {"type": "date"}
                self.instance.indices.put_alias(index=self.index,
                                                name=index,
                                                body=mapping)
                while self.instance.count(index=self.index) != self.instance.count(index=index):
                    logging.info("Waiting for date indexed data to be indexed...")
                    time.sleep(1)

        results = helpers.scan(self.instance, index=index, scroll='5m',
                                     query={"query":
                                                {"range":
                                                    {year_field:
                                                        {"gte": start_year,
                                                         "lte": end_year}}}})

        for result in results:
            yield result["_id"], result['_source'][self.content_field]

    def save(self, filename, saved_data=None):
        if saved_data is None:
            saved_data = {"host": self.host, "port": self.port, "index": self.index,
                          "content_field": self.content_field, "username": self.username,
                          "password": self.password, "doc_type":self.doc_type, "query": self.query}
        return super(ElasticSearchCorpus, self).save(filename, saved_data)


class DictionaryCorpus(CorpusInterface):
    def __init__(self, content_field, iterable=None, generate_id=True, reference_field=None):
        super(DictionaryCorpus, self).__init__()
        self.content_field = content_field
        self._documents = []
        self.idx = 0
        active_field = None
        if reference_field:
            self.reference_field = reference_field
            active_field = content_field
            content_field = reference_field
        else:
            self.reference_field = content_field
        if iterable:
            self.import_from_iterable(iterable, content_field, generate_id)
        if active_field:
            self.content_field = active_field


    @classmethod
    def class_key(cls):
        return "dictionary"

    def __iter__(self):
        for doc in self._documents:
            yield doc["_id"], doc["_source"][self.content_field]

    def __len__(self):
        return len(self._documents)

    def append_to_record(self, record_id, field_name, field_value):
        for doc in self._documents:
            if doc["_id"] == record_id:
                doc["_source"][field_name] = field_value
                return
        raise ValueError("No record with id '{}' was found.".format(record_id))

    def get_field(self, field=None):
        """Get a different field to iterate over, keeping all other details."""
        if not field:
            field = self.content_field
        return DictionaryCorpus(content_field=field, iterable=self._documents,
                                generate_id=False, reference_field=self.content_field)

    def get_generator_without_id(self, field=None):
        if not field:
            field = self.content_field
        for doc in self._documents:
            yield doc["_source"][field]

    def import_from_iterable(self, iterable, content_field, generate_id=True):
        """
        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        """
        if generate_id:
            self._documents = [{"_id": hash(doc[content_field]),
                                "_source": doc} for doc in iterable]
            self.reference_field = content_field
        else:
            self._documents = [item for item in iterable]

    # TODO: generalize for datetimes
    # TODO: validate input data to ensure that it has valid year data
    def get_data_by_year(self, start_year, end_year, year_field="year"):
        for result in self._documents:
            if start_year <= int(result["_source"][year_field]) <= end_year:
                yield result["_id"], result["_source"][self.content_field]

    def save(self, filename, saved_data=None):
        if saved_data is None:
            saved_data = {"reference_field": self.reference_field, "content_field": self.content_field,
                          "iterable": [doc["_source"] for doc in self._documents]}
        return super(DictionaryCorpus, self).save(filename, saved_data)

# Collection of output formats: people put files, folders, etc in, and they can choose from these to be the output
# These consume the iterable collection of dictionaries produced by the various iter_ functions.
output_formats = {cls.class_key(): cls for cls in [ElasticSearchCorpus, DictionaryCorpus]}


def load_persisted_corpus(filename):
    with open(filename+"_CORPUS") as f:
        data_dict = json.load(f)
    return output_formats[data_dict['class']](**data_dict["saved_data"])
