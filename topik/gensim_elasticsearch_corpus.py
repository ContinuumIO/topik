from gensim.corpors.textcorpus import TextCorpus
from elasticsearch import Elasticsearch, helpers


class ElasticSearchCorpus(TextCorpus):
    def __init__(self, host, index, text_field, port=9200, username=None,
                 password=None, doc_type=None, query=None):
        super(ElasticSearchCorpus, self).__init__()
        self.instance = Elasticsearch(host)
        self.index = index
        self.text_field = text_field

    def get_texts(self):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query)
        for result in results:
            yield result['_source'][self.text_field]
