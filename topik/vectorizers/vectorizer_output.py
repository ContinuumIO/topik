import itertools

def _accumulate_terms(tokenized_corpora):
    global_terms=set()
    document_term_counts = {}
    for id, doc in tokenized_corpora:
        doc_terms = set(doc)
        global_terms.update(doc_terms)
        document_term_counts[id] = len(doc_terms)
    return global_terms, document_term_counts


class VectorizerOutput(object):
    def __init__(self, tokenized_corpora, vectorizer_func):
        iter1, iter2 = itertools.tee(tokenized_corpora)
        self._global_terms, self._document_term_counts = _accumulate_terms(iter1)
        self._id_term_map = {id: term for id, term in enumerate(self._global_terms)}
        self._term_id_map = {term: id for id, term in enumerate(self._global_terms)}
        self._vectors = vectorizer_func(iter2, self)

    def __iter__(self):
        for id, vector in self._vectors.items():
            yield id, vector

    def __len__(self):
        return len(self._vectors)

    @property
    def global_term_count(self):
        return len(self._global_terms)

    @property
    def term_id_map(self):
        return self._term_id_map

    @property
    def id_term_map(self):
        return self._id_term_map

    @property
    def document_term_counts(self):
        return self._document_term_counts

    @property
    def vectors(self):
        return self._vectors
