from six.moves import UserDict
import logging
import time

from elasticsearch import Elasticsearch, helpers

from ._registry import register_output
from .base_output import OutputInterface
from topik.vectorizers.vectorizer_output import VectorizerOutput
from topik.models.base_model_output import ModelOutput

def es_setitem(key, value, doc_type, instance, index, batch_size=1000):
    """load an iterable of (id, value) pairs to the specified new or
           new or existing field within existing documents."""
    batch = []
    for id, val in value:
        action = {'_op_type': 'update',
                  '_index': index,
                  '_type': doc_type,
                  '_id': id,
                  'doc': {key: val},
                  'doc_as_upsert': "true",
                  }
        batch.append(action)
        if len(batch) >= batch_size:
            helpers.bulk(client=instance, actions=batch,
                         index=index)
            batch = []
    if batch:
        helpers.bulk(client=instance, actions=batch, index=index)
    instance.indices.refresh(index)

def es_getitem(key, doc_type, instance, index, query=None):
    results = helpers.scan(instance, index=index,
                               query=query, doc_type=doc_type)
    for result in results:
        try:
            id = int(result["_id"])
        except ValueError:
            id = result["_id"]
        yield id, result['_source'][key]

class BaseElasticCorpora(UserDict):
    def __init__(self, instance, index, corpus_type, query=None,
                 batch_size=1000):
        self.instance = instance
        self.index = index
        self.corpus_type = corpus_type
        self.query = query
        self.batch_size = batch_size
        pass

    def __setitem__(self, key, value):
        es_setitem(key, value, self.corpus_type, self.instance, self.index)


    def __getitem__(self, key):
        return es_getitem(key,self.corpus_type,self.instance,self.index,
                          self.query)

class VectorizedElasticCorpora(BaseElasticCorpora):
    def __setitem__(self, key, value):
        #id_term_map
        es_setitem(key,value.id_term_map.items(),"term",self.instance,self.index)
        #document_term_counts
        es_setitem(key,value.document_term_counts.items(),"document_term_count",self.instance,self.index)
        #doc_lengths
        es_setitem(key,value.doc_lengths.items(),"document_length",self.instance,self.index)
        #global term_frequency
        es_setitem(key,value.term_frequency.items(),"term_frequency",self.instance,self.index)
        #vectors
        es_setitem(key,value.vectors.items(),"vector",self.instance,self.index)
        # could either upload vectors explicitly here (above) or using Super (below)
        #super(VectorizedElasticCorpora, self).__setitem__(key, value)

    def __getitem__(self, key):
        # TODO: each of these should be retrieved from a query.  Populate the VectorizerOutput object
        # and return it.  These things can be iterators instead of dicts; VectorizerOutput should
        # not care.
        # TODO: this is the id->term map for the full set of unique terms across all docs
        id_term_map = {int(term_id): term for term_id, term in es_getitem(key,"term",self.instance,self.index,self.query)}
        # 15
        # TODO: this is the count of terms associated with each document
        document_term_count = {int(doc_id): doc_term_count for doc_id, doc_term_count in es_getitem(key,"document_term_count",self.instance,self.index,self.query)}
        # {"doc1": 3, "doc2": 5}
        doc_lengths = {int(doc_id): doc_length for doc_id, doc_length in es_getitem(key,"document_length",self.instance,self.index,self.query)}
        term_frequency = {int(term_id): global_frequency for term_id, global_frequency in es_getitem(key,"term_frequency",self.instance,self.index,self.query)}
        # TODO: this is the vectorized representation of each document
        vectors = {int(doc_id): {int(term_id): term_weight for term_id, term_weight in doc_term_weights.items()} for doc_id, doc_term_weights in es_getitem(key,"vector",self.instance,self.index,self.query)}
        #vectors = {int(doc_id): {doc_term_weights for doc_id, doc_term_weights in es_getitem(key,"vector",self.instance,self.index,self.query)}
        #vectors = list(es_getitem(key,"vector",self.instance,self.index,self.query))
        #  {"doc1": {1: 3, 2: 1}  # word id is key, word count is value (for bag of words model)
        return VectorizerOutput(id_term_map=id_term_map,
                                document_term_counts=document_term_count,
                                doc_lengths=doc_lengths,
                                term_frequency=term_frequency,
                                vectors=vectors)

class ModeledElasticCorpora(BaseElasticCorpora):
    def __setitem__(self, key, value):
        es_setitem(key,value.vocab.items(),"term",self.instance,self.index)
        es_setitem(key,value.term_frequency.items(),"term_frequency",self.instance,self.index)
        es_setitem(key,value.topic_term_matrix.items(),"topic_term_dist",self.instance,self.index)
        es_setitem(key,value.doc_lengths.items(),"doc_length",self.instance,self.index)
        es_setitem(key,value.doc_topic_matrix.items(),"doc_topic_dist",self.instance,self.index)

    def __lt__(self, y):
        return super(ModeledElasticCorpora, self).__lt__(y)

    def __getitem__(self, key):
        vocab = {int(term_id): term for term_id, term in \
                 es_getitem(key,"term",self.instance,self.index,self.query)}
        term_frequency = {int(term_id): tf for term_id, tf in \
                          es_getitem(key,"term_frequency",self.instance,self.index,self.query)}
        topic_term_matrix = {topic_id: topic_term_dist for topic_id, topic_term_dist in \
                             es_getitem(key,"topic_term_dist",self.instance,self.index,self.query)}
        doc_lengths = {topic_id: doc_length for topic_id, doc_length in \
                       es_getitem(key,"doc_length",self.instance,self.index,self.query)}
        doc_topic_matrix = {int(doc_id): doc_topic_dist for doc_id, doc_topic_dist in \
                             es_getitem(key,"doc_topic_dist",self.instance,self.index,self.query)}
        return ModelOutput(vocab=vocab, term_frequency=term_frequency,
                           topic_term_matrix=topic_term_matrix,
                           doc_lengths=doc_lengths,
                           doc_topic_matrix=doc_topic_matrix)

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
        self.hash_field = hash_field
        if iterable:
            self.import_from_iterable(iterable, hash_field)
        self.filter_expression = filter_expression

        self.tokenized_corpora = tokenized_corpora if tokenized_corpora else \
            BaseElasticCorpora(self.instance, self.index, 'tokenized', self.query)
        self.vectorized_corpora = vectorized_corpora if vectorized_corpora else \
            VectorizedElasticCorpora(self.instance, self.index, 'vectorized', self.query)
        self.modeled_corpora = modeled_corpora if modeled_corpora else \
            ModeledElasticCorpora(self.instance, self.index, "models", self.query)


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
        if self.instance.indices.get_field_mapping(fields=[field],
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

