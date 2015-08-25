from gensim.corpora.textcorpus import TextCorpus
from topik.utils import _iter_corpus


class DigestedDocumentCollection(TextCorpus):
    """A bag-of-words representation of a corpus (collection of documents).

    This serves as direct input to modeling functions.  It is output from
    preprocessing functions.

    Parameters
    ----------
    corpus: A collection of tokenized documents
        Each document is a list of tokens, tokenized and normalized strings
        (either utf8 or unicode) (e.g. output of topik.SimpleTokenizer)

    Readers iterate over tuples (id, content)

    >>> id_documents = iter_document_json_stream(
            './topik/tests/data/test-data-1', "text")
    >>> ids, texts = unzip(id_documents)
    >>> my_corpus = SimpleTokenizer(texts)
    >>> corpus_bow = CorpusBOW(my_corpus)

    """
    def __init__(self, tokenized_corpus, word_dict):
        self.corpus = tokenized_corpus
        self.dict = word_dict

    def get_texts(self):
        """Each iteration gets a tokenized document from the corpus"""
        for tokens in _iter_corpus(self.corpus):
            yield self.dict.doc2bow(tokens)

    def get_id2word_dict(self):
        return self.dict
