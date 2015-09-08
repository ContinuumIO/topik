from itertools import tee

from gensim.interfaces import CorpusABC
from gensim.corpora.dictionary import Dictionary


# Doctest-only imports


class DigestedDocumentCollection(CorpusABC):
    """A bag-of-words representation of a corpus (collection of documents).

    This serves as direct input to modeling functions.  It is output from
    preprocessing functions.

    Parameters
    ----------
    corpus: A collection of tokenized documents
        Each document is a list of tokens, tokenized and normalized strings
        (either utf8 or unicode) (e.g. output of topik.SimpleTokenizer)

    Readers iterate over tuples (id, content)

    """
    def __init__(self, tokenized_corpus):
        self.corpus, corpus_for_dict = tee(tokenized_corpus)
        self.dict = Dictionary(corpus_for_dict)
        super(DigestedDocumentCollection, self).__init__()

    def __iter__(self):
        for doc_tokens in self.corpus:
            yield self.dict.doc2bow(doc_tokens)

    def get_texts(self):
        """Each iteration gets a tokenized document from the corpus"""
        for tokens in self.corpus:
            yield self.dict.doc2bow(tokens)

    def get_id2word_dict(self):
        return self.dict
