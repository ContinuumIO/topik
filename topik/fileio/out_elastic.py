import logging
import time

from elasticsearch import Elasticsearch, helpers

from ._registry import register_output
from .base_output import OutputInterface

class BaseElasticCorpus(dict):
    def __init__(self, instance, index, corpus_type, query=None,
                 batch_size=1000):
        self.instance = instance
        self.index = index
        self.corpus_type = corpus_type
        self.query = query
        self.batch_size = batch_size
        pass

    def __setitem__(self, key, value):
        """load an iterable of (id, value) pairs to the specified new or
           new or existing field within existing documents."""
        batch = []
        print('elasticsetitem')
        print(key)
        print(type(value))
        for doc_id, val in value:
            #print(str(key)+' | '+str(type(val))+' | '+self.corpus_type+' | '+str(val))
            action = {'_op_type': 'update',
                      '_index': self.index,
                      '_type': self.corpus_type,
                      '_id': doc_id,
                      'doc': {key: val},
                      'doc_as_upsert': "true",
                      }
            batch.append(action)
            if len(batch) >= self.batch_size:
                helpers.bulk(client=self.instance, actions=batch,
                             index=self.index)
                batch = []
        if batch:
            helpers.bulk(client=self.instance, actions=batch, index=self.index)
        self.instance.indices.refresh(self.index)

    def __getitem__(self, field):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.corpus_type)
        for result in results:
            yield result["_id"], result['_source'][field]

class VectorizedElasticCorpus(BaseElasticCorpus):
    def __setitem__(self, key, value):
        raise NotImplementedError
        #for prop in value.properties
        #   upload that
        #super()
    def __getitem__(self, item):
        raise NotImplementedError
    @property
    def global_term_count(self):
        raise NotImplementedError

class ModeledElasticCorpus(BaseElasticCorpus):
    def __setitem__(self, key, value):
        raise NotImplementedError

@register_output
class ElasticSearchOutput(OutputInterface):
    def __init__(self, source, index, hash_field=None, doc_type='continuum',
                 query=None, iterable=None, filter_expression="",
                 vectorized_corpora=None, tokenized_corpora=None, modeled_corpora=None,
                 **kwargs):
        super(ElasticSearchOutput, self).__init__()
        self.hosts = source
        self.instance = Elasticsearch(hosts=source, **kwargs)
        self.index = index
        self.doc_type = doc_type
        self.query = query
        if iterable:
            self.import_from_iterable(iterable, hash_field)
        self.filter_expression = filter_expression

        self.tokenized_corpora = tokenized_corpora if tokenized_corpora else \
            BaseElasticCorpus(self.instance, self.index, 'tokenized', self.query)
        self.vectorized_corpora = vectorized_corpora if vectorized_corpora else \
            BaseElasticCorpus(self.instance, self.index, 'vectorized', self.query)
        self.modeled_corpora = modeled_corpora if modeled_corpora else \
            BaseElasticCorpus(self.instance, self.index, "models", self.query)


    @property
    def filter_string(self):
        return self.filter_expression

    def import_from_iterable(self, iterable, field_to_hash='text', batch_size=500):
        """Load data into Elasticsearch from iterable.

        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        field_to_hash: string identifier of field to hash for content ID.  For
            list of dicts, a valid key value in the dictionary is required. For
            list of strings, a dictionary with one key, "text" is created and
            used.
        """
        if field_to_hash:
            self.hash_field = field_to_hash
            batch = []
            for item in iterable:
                if isinstance(item, basestring):
                    item = {field_to_hash: item}
                id = hash(item[field_to_hash])
                action = {'_op_type': 'update',
                          '_index': self.index,
                          '_type': self.doc_type,
                          '_id': id,
                          'doc': item,
                          'doc_as_upsert': "true",
                          }
                batch.append(action)
                if len(batch) >= batch_size:
                    helpers.bulk(client=self.instance, actions=batch, index=self.index)
                    batch = []
            if batch:
                helpers.bulk(client=self.instance, actions=batch, index=self.index)
            self.instance.indices.refresh(self.index)
        else:
            raise ValueError("A field_to_hash is required for import_from_iterable")

    def convert_date_field_and_reindex(self, field):
        index = self.index
        if self.instance.indices.get_field_mapping(field=field,
                                           index=index,
                                           doc_type=self.doc_type) != 'date':
            index = self.index+"_{}_alias_date".format(field)
            if not self.instance.indices.exists(index) or self.instance.indices.get_field_mapping(field=field,
                                           index=index,
                                           doc_type=self.doc_type) != 'date':
                mapping = self.instance.indices.get_mapping(index=self.index,
                                                            doc_type=self.doc_type)
                mapping[self.index]["mappings"][self.doc_type]["properties"][field] = {"type": "date"}
                self.instance.indices.put_alias(index=self.index,
                                                name=index,
                                                body=mapping)
                self.instance.indices.refresh(index)
                while self.instance.count(index=self.index) != self.instance.count(index=index):
                    logging.info("Waiting for date indexed data to be indexed...")
                    time.sleep(1)
        return index

    # TODO: validate input data to ensure that it has valid year data
    def get_date_filtered_data(self, field_to_get, start, end, filter_field="date"):
        converted_index = self.convert_date_field_and_reindex(field=filter_field)

        results = helpers.scan(self.instance, index=converted_index,
                               doc_type=self.doc_type, query={
            "query": {"filtered": {"filter": {"range": {filter_field: {
                "gte": start,"lte": end}}}}}})
        for result in results:
            yield result["_id"], result['_source'][field_to_get]

    def get_filtered_data(self, field_to_get, filter=""):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.doc_type)
        for result in results:
            yield result["_id"], result['_source'][field_to_get]

    def save(self, filename, saved_data=None):
        if saved_data is None:
            saved_data = {"source": self.hosts, "index": self.index, "hash_field": self.hash_field,
                          "doc_type": self.doc_type, "query": self.query}
        return super(ElasticSearchOutput, self).save(filename, saved_data)

    def synchronize(self, max_wait, field):
        # TODO: change this to a more general condition for wider use, including read_input
        # could just pass in a string condition and then 'while not eval(condition)'
        count_not_yet_updated = -1
        while count_not_yet_updated != 0:
            count_not_yet_updated = self.instance.count(index=self.index,
                                             doc_type=self.doc_type,
                                             body={"query": {
                                                        "constant_score" : {
                                                            "filter" : {
                                                                "missing" : {
                                                                    "field" : field}}}}})['count']
            logging.debug("Count not yet updated: {}".format(count_not_yet_updated))
            time.sleep(0.01)
        pass

