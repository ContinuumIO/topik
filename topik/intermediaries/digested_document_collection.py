import gensim

class DigestedDocumentCollection(gensim.interfaces.CorpusABC):
    """A bag-of-words representation of a corpus (collection of documents).

    This serves as direct input to modeling functions.  It is output from
    preprocessing functions.

    Parameters
    ----------
    corpus: A collection of tokenized documents
        Each document is a list of tokens, tokenized and normalized strings
        (either utf8 or unicode) (e.g. output of topik.SimpleTokenizer)

    Readers iterate over tuples (id, content), but discard id in return (for compatibility with Gensim.)

    """
    def __init__(self, tokenized_corpus):
        from gensim.corpora.dictionary import Dictionary
        self._corpus = tokenized_corpus
        self._dict = Dictionary(tokenized_corpus.get_generator_without_id())
        super(DigestedDocumentCollection, self).__init__()

    def __iter__(self):
        """Discards id field - for compatibility with Gensim."""
        for _id, doc_tokens in self._corpus:
            yield self._dict.doc2bow(doc_tokens)

    def __len__(self):
        return len(self._corpus)

    def get_id2word_dict(self):
        return self._dict

    def save(self, filename):
        self._corpus.save(filename)

    @property
    def persistor(self):
        return self._corpus.persistor

    @property
    def filter_string(self):
        return self._corpus.filter_string
