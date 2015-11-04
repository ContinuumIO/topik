from abc import abstractproperty

def _accumulate_terms(tokenized_data):
    global_terms=set()
    document_term_counts = {}
    for id, doc in tokenized_data:
        doc_terms = set(doc)
        global_terms = global_terms.update(doc_terms)
        document_term_counts[id] = len(doc_terms)
    return global_terms, document_term_counts


class VectorizerOutput(object):
    def __init__(self, tokenized_data, vectorizer_func):
        self._global_terms, self._document_term_counts = _accumulate_terms(tokenized_data)
        self._id_term_map = {id: term for id, term in enumerate(self._global_terms)}
        self._term_id_map = {term: id for id, term in enumerate(self._global_terms)}
        self._vectors = vectorizer_func(tokenized_data, self)

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

    @abstractproperty
    def vectors(self):
        return self._vectors
