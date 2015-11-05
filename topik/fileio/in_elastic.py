import logging
import time

from ._registry import register_input, register_output
from .base_output import OutputInterface


@register_input
def elastic(hosts, **kwargs):
    """Iterate over all documents in the specified elasticsearch intance and index that match the specified query.

    kwargs are passed to Elasticsearch class instantiation, and can be used to pass any additional options
    described at https://elasticsearch-py.readthedocs.org/en/master/

    Parameters
    ----------
    hosts : str or list
        Address of the elasticsearch instance any index.  May include port, username and password.
        See https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch for all options.

    content_field : str
        The name fo the field that contains the main text body of the document.

    **kwargs: additional keyword arguments to be passed to Elasticsearch client instance and to scan query.
              See
              https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch for all client options.
              https://elasticsearch-py.readthedocs.org/en/master/helpers.html#elasticsearch.helpers.scan for all scan options.
    """

    from elasticsearch import Elasticsearch, helpers
    es = Elasticsearch(hosts, **kwargs)
    results = helpers.scan(es, **kwargs)
    for result in results:
        yield result['_source']


@register_output
class ElasticSearchOutput(OutputInterface):
    def __init__(self, source, index, content_field, doc_type='continuum', query=None, iterable=None,
                 filter_expression="", **kwargs):
        #from elasticsearch import Elasticsearch
        import elasticsearch
        print(dir(elasticsearch))
        super(ElasticSearchOutput, self).__init__()
        self.hosts = source
        self.instance = elasticsearch.Elasticsearch(hosts=source, **kwargs)
        self.index = index
        self.content_field = content_field
        self.doc_type = doc_type
        self.query = query
        if iterable:
            self.import_from_iterable(iterable, content_field)
        self.filter_expression = filter_expression

    # TODO: are these still useful now that we have decorator registers?
    @classmethod
    def class_key(cls):
        return "elastic"

    @property
    def filter_string(self):
        return self.filter_expression

    def __iter__(self):
        from elasticsearch import helpers
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.doc_type)
        for result in results:
            yield result["_id"], result['_source'][self.content_field]

    def __len__(self):
        return self.instance.count(index=self.index, doc_type=self.doc_type)["count"]

    def get_generator_without_id(self, field=None):
        if not field:
            field = self.content_field
        for (_, result) in ElasticSearchOutput(self.hosts, self.index, field, self.doc_type, self.query):
            yield result

    def append_to_record(self, record_id, field_name, field_value):
        self.instance.update(index=self.index, id=record_id, doc_type=self.doc_type,
                             body={"doc": {field_name: field_value}})

    def get_field(self, field=None):
        """Get a different field to iterate over, keeping all other
           connection details."""
        if not field:
            field = self.content_field
        return ElasticSearchOutput(self.hosts, self.index, field, self.doc_type, self.query)

    def import_from_iterable(self, iterable, content_field='text', batch_size=500):
        """Load data into Elasticsearch from iterable.

        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        content_field: string identifier of field to hash for content ID.  For
            list of dicts, a valid key value in the dictionary is required. For
            list of strings, a dictionary with one key, "text" is created and
            used.
        """
        from elasticsearch import helpers
        batch = []
        for item in iterable:
            if isinstance(item, basestring):
                item = {content_field: item}
            id = hash(item[content_field])
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
    def get_date_filtered_data(self, start, end, filter_field="date"):
        converted_index = self.convert_date_field_and_reindex(field=filter_field)
        return ElasticSearchOutput(self.hosts, converted_index, self.content_field, self.doc_type,
                                   query={"query": {"filtered": {"filter": {"range": {filter_field: {"gte": start,
                                                                                              "lte": end}}}}}},
                                   filter_expression=self.filter_expression + "_date_{}_{}".format(start, end))

    def get_filtered_corpus(self, filter=""):
        raise NotImplementedError

    def save(self, filename, saved_data=None):
        if saved_data is None:
            saved_data = {"source": self.hosts, "index": self.index, "content_field": self.content_field,
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

