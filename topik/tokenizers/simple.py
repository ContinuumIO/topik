import gensim
import logging
# imports used only for doctests
from topik.tokenizers._registry import register


def _simple_document(text, min_length=1, stopwords=None):
    """A text tokenizer that simply lowercases, matches alphabetic
    characters and removes stopwords.  For use on individual text documents.

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    min_length : int
        Minimum length of any single word
    stopwords: None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> text = "frank FRANK the frank dog cat"
    >>> tokenized_text = _simple_document(text)
    >>> tokenized_text == ["frank", "frank", "frank", "dog", "cat"]
    True
    """
    if not stopwords:
        from gensim.parsing.preprocessing import STOPWORDS as stopwords
    #logging.debug("Tokenizing text: {}".format(text))
    return [word for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords and len(word) >= min_length]


@register
def simple(raw_corpus, min_length=1, stopwords=None):
    """A text tokenizer that simply lowercases, matches alphabetic
    characters and removes stopwords.

    Parameters
    ----------
    raw_corpus : iterable of tuple of (doc_id(str/int), doc_text(str))
        body of documents to examine
    min_length : int
        Minimum length of any single word
    stopwords: None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> sample_corpus = [("doc1", "frank FRANK the frank dog cat"),
    ...               ("doc2", "frank a dog of the llama")]
    >>> tokenized_corpora = simple(sample_corpus)
    >>> next(tokenized_corpora) == ("doc1",
    ... ["frank", "frank", "frank", "dog", "cat"])
    True
    """
    for doc_id, doc_text in raw_corpus:
        # logging.debug("Tokenizing doc_id: {}".format(doc_id))
        yield(doc_id, _simple_document(doc_text, min_length=min_length, stopwords=stopwords))