from gensim.corpora.textcorpus import TextCorpus
from elasticsearch import Elasticsearch, helpers


class ElasticSearchCorpus(TextCorpus):
    def __init__(self, host, index, content_field, port=9200, username=None,
                 password=None, doc_type=None, query=None):
        super(ElasticSearchCorpus, self).__init__()
        self.instance = Elasticsearch(host)
        self.index = index
        self.content_field = content_field

    def get_texts(self):
        results = helpers.scan(self.instance, index=self.index,
                               query=self.query)
        for result in results:
            yield result['_source'][self.content_field]
