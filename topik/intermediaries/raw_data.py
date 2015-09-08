"""
This file is concerned with providing a simple interface for data stored in
Elasticsearch.  The class(es) defined here are fed into the preprocessing step.
"""

import logging
import time

from elasticsearch import Elasticsearch, helpers


def _get_hash_identifier(input_data, id_field):
    return hash(input_data[id_field])


class ElasticSearchCorpus(object):
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

    def __iter__(self):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.doc_type)
        for result in results:
            yield result["_id"], result['_source'][self.content_field]

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
        # TODO: is there a good way to do bulk without forcing in-memory of whole data?
        # helpers.bulk(self.instance, )

    def get_number_of_items_stored(self):
        return self.instance.count(index=self.index, doc_type=self.doc_type)['count']

    # TODO: generalize for datetimes
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


class DictionaryCorpus(object):
    def __init__(self, content_field, iterable=None, generate_id=True):
        super(DictionaryCorpus, self).__init__()
        self.content_field = content_field
        self._documents = []
        self.idx = 0
        if iterable:
            self.import_from_iterable(iterable, content_field, generate_id)

    def __iter__(self):
        for doc in self._documents:
            yield doc["_id"], doc["_source"][self.content_field]

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
                                generate_id=False)

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
        else:
            self._documents = [item for item in iterable]

    def get_number_of_items_stored(self):
        return len(self._documents)

    # TODO: generalize for datetimes
    # TODO: validate input data to ensure that it has valid year data
    def get_data_by_year(self, start_year, end_year, year_field="year"):
        for result in self._documents:
            if start_year <= int(result["_source"][year_field]) <= end_year:
                yield result["_id"], result["_source"][self.content_field]


# Collection of output formats: people put files, folders, etc in, and they can choose from these to be the output
# These consume the iterable collection of dictionaries produced by the various iter_ functions.
output_formats = {"elasticsearch": ElasticSearchCorpus,
                  "dictionary": DictionaryCorpus,
                  }
