from __future__ import absolute_import

import logging
import itertools

import gensim

def iter_corpus(corpus):
    for document in corpus:
        yield document


class CorpusBOW(object):
    """A bag-of-words representation of a corpus (collection of documents).

    Parameters
    ----------
    corpus: A collection of documents
        Each document is a list of tokens, tokenized and normalized strings 
        (either utf8 or unicode) (e.g. topik.SimpleTokinizer)

    Readers iterate over tuples (id, content)

    >>> id_documents = iter_document_json_stream(
            './topik/tests/data/test-data-1', "text")
    >>> ids, texts = unzip(id_documents)
    >>> my_corpus = SimpleTokenizer(texts)
    >>> corpus_bow = CorpusBOW(my_corpus)

    """
    def __init__(self, corpus):
        self.corpus = corpus
        self.iter_1, self.iter_2 = itertools.tee(self.corpus, 2)
        self.tokens = [tokens for tokens in iter_corpus(self.iter_1)]
        # Create dictionary out of input corpus tokens
        self.dict = gensim.corpora.Dictionary(self.tokens)
        self.filename = None

    def __iter__(self):
        for tokens in iter_corpus(self.iter_2):
            yield self.dict.doc2bow(tokens)

    def serialize(self, filename):
        """Serialize a corpus (collection of documents) in a bag-of-words vector space to a Matrix Market Exchange Format.

        References
        ----------
        [1]_.

        .. [1] http://math.nist.gov/MatrixMarket/formats.html

        Parameters
        ----------
        filename: string
            The filename for the stored serialized corpus

        >>> id_documents = iter_document_json_stream('./topik/tests/data/test-data-1', "text")
        >>> ids, texts = unzip(id_documents)
        >>> my_corpus = SimpleTokenizer(texts)
        >>> corpus_bow = CorpusBOW(my_corpus)
        >>> corpus_bow.serialize("my_serialized_corpus")

        """
        # Serialize and save corpus bag of words
        corpus = gensim.corpora.MmCorpus.serialize(filename, self)
        self.filename = filename
        return self.filename

    def save_dict(self, filename):
        """Store the dictionary to a file

        filename: string
            The desired filename for the generated dictionary

        >>> id_documents = iter_document_json_stream('./topik/tests/data/test-data-1', "text")
        >>> id, texts = unzip(id_documents)
        >>> my_corpus = SimpleTokenizer(texts)
        >>> corpus_bow = CorpusBOW(my_corpus)
        >>> corpus_bow.save_dict("my_corpus_dictionary")

        """
        logging.info("storing dictionary to %s" % filename)
        self.dict.save(filename)

        return self.dict
