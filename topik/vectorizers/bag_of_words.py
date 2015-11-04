from collections import Counter
from ._registry import register
from vectorizer_output import VectorizerOutput

def _count_words_in_docs(tokenized_data, vectorizer_output):
    doc_counts = {}
    for id, doc in tokenized_data:
        doc_counts[id] = {vectorizer_output.term_id_map[key]: value for key, value in Counter(doc)}
    return doc_counts

@register
def bag_of_words(tokenized_data, global_terms, document_term_counts):
    return VectorizerOutput(tokenized_data, _count_words_in_docs)