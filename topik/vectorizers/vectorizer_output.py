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
    def __init__(self, tokenized_corpora=None, vectorizer_func=None, global_terms=None,
                 document_term_counts=None, vectors=None):
        if tokenized_corpora and vectorizer_func:
            iter1, iter2 = itertools.tee(tokenized_corpora)
            self._global_terms, self._document_term_counts = _accumulate_terms(iter1)
        elif global_terms and document_term_counts and vectors:
            self._global_terms = global_terms
            self._document_term_counts = document_term_counts
            self._vectors = vectors
        else:
            raise ValueError("Must provide either tokenized corpora and vectorizer func, "
                             "or global term collection, document term counts, and vectors.")
            self._global_terms = []
        self.id_term_map = {id: term for id, term in enumerate(self._global_terms)}
        self.term_id_map = {term: id for id, term in enumerate(self._global_terms)}
        # Needs to be here because term map may be used in vectorization
        if not vectors and vectorizer_func:
            self._vectors = vectorizer_func(iter2, self)
        else:
            raise ValueError("Need to provide either vectors or vectorizer_func")

    def __iter__(self):
        for id, vector in self._vectors.items():
            yield id, vector

    def __len__(self):
        return len(self._vectors)

    @property
    def global_term_count(self):
        return len(self._global_terms)

    @property
    def document_term_counts(self):
        return self._document_term_counts

    @property
    def vectors(self):
        return self._vectors
