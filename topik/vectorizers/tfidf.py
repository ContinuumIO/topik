from collections import Counter
from ._registry import register
from vectorizer_output import VectorizerOutput

def _count_words_in_docs(tokenized_data, vectorizer_output):
    doc_counts = {}
    for id, doc in tokenized_data:
        raise NotImplementedError
        # code below here is copied from bag of words, left here for example.
        doc_counts[id] = {vectorizer_output.term_id_map[key]: value for key, value in Counter(doc).items()}
    return doc_counts

@register
def tfidf(tokenized_data):
    return VectorizerOutput(tokenized_data, _count_words_in_docs)
