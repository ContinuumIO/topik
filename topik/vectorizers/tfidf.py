from math import log
from ._registry import register
from vectorizer_output import VectorizerOutput
from .bag_of_words import _count_words_in_docs


def _count_document_occurences(doc_counts, total_words):
    return {word_id: sum(1 for doc in doc_counts.values() if word_id in doc)
            for word_id in range(total_words)}


def _calculate_tfidf(tokenized_corpus, vectorizer_output):
    tokens = list(tokenized_corpus)
    doc_counts = _count_words_in_docs(tokens, vectorizer_output)
    document_occurrences = _count_document_occurences(doc_counts, vectorizer_output.global_term_count)
    idf = {word_id: log(len(tokens) / (document_occurrences[word_id]))
           for word_id in range(vectorizer_output.global_term_count)}
    tf_idf = {}
    # TODO: this is essentially a sparse matrix multiply and could be done much more efficiently
    for id, doc in doc_counts.items():
        tf_idf[id] = {}
        for word_id, count in doc.items():
            tf_idf[id].update({word_id: count*idf[word_id]})
    return tf_idf


@register
def tfidf(tokenized_corpus):
    return VectorizerOutput(tokenized_corpus, _calculate_tfidf)
