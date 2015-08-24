"""
This file is concerned with providing a simple interface for data stored in
Elasticsearch.  The class(es) defined here are fed into the preprocessing step.
"""

from elasticsearch import Elasticsearch, helpers


def _get_hash_identifier(input_data, id_field):
    return hash(input_data[id_field])


class ElasticSearchCorpus(object):
    def __init__(self, host, index, text_field, port=9200, username=None,
                 password=None, doc_type=None, query=None):
        super(ElasticSearchCorpus, self).__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.instance = Elasticsearch(hosts=[{"host": host, "port": port,
                                              "http_auth": "{}:{}".format(username, password)}
                                             ])
        self.index = index
        self.text_field = text_field
        self.doc_type = doc_type
        self.query = query

    def __iter__(self):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query, doc_type=self.doc_type)
        for result in results:
            yield result['_source'][self.text_field]

    def append_to_record(self, record_id, field_name, field_value):
        self.instance.update(index=self.index, id=record_id,
                             body={"doc": {field_name: field_value}})

    def get_field(self, field=None):
        """Get a different field to iterate over, keeping all other
           connection details."""
        if not field:
            field = self.text_field
        return ElasticSearchCorpus(self.host, self.index, field, self.port,
                                   self.username, self.password, self.doc_type,
                                   self.query)

    def import_from_iterable(self, iterable, id_field="text"):
        """Load data into Elasticsearch from iterable.

        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        id_field: string identifier of field to hash for content ID.  For
            list of dicts, a valid key value in the dictionary is required. For
            list of strings, a dictionary with one key, "text" is created and
            used.
        """
        for item in iterable:
            if isinstance(item, basestring):
                item = {"text": item}
            id = _get_hash_identifier(item, id_field)
            self.instance.index(index=self.index, doc_type="continuum",
                                id=id, body=item)
        # TODO: is there a good way to do bulk without forcing in-memory of whole data?
        # helpers.bulk(self.instance, )
