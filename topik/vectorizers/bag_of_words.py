from collections import Counter
from ._registry import register
from vectorizer_output import VectorizerOutput

def _count_words_in_docs(tokenized_corpora, vectorizer_output):
    doc_counts = {}
    for id, doc in tokenized_corpora:
        doc_counts[id] = {vectorizer_output.term_id_map[key]: value
                          for key, value in Counter(doc).items()}
    return doc_counts

@register
def bag_of_words(tokenized_corpora):
    return VectorizerOutput(tokenized_corpora, _count_words_in_docs)