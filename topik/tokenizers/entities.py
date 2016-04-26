import logging
import itertools
from textblob import TextBlob

from topik.tokenizers.simple import _simple_document

# imports used only for doctests
from topik.tokenizers._registry import register

sample_corpus = [
            ("doc1", str(u"Frank the Swank-Tank walked his sassy unicorn, Brony,"
                         u" to prancercise class daily.  Prancercise was "
                         u"a tremendously popular pastime of sassy "
                         u"unicorns and retirees alike.")),
            ("doc2", str(u"Prancercise is a form of both art and fitniss, "
                         u"originally invented by sassy unicorns. It has "
                         u"recently been popularized by such retired "
                         u"celebrities as Frank The Swank-Tank."))]

def _collect_entities(raw_corpus, freq_min=2, freq_max=10000):
    """Return noun phrases from collection of documents.

    Parameters
    ----------
    raw_corpus: Corpus-base derived object or iterable collection of raw text
    freq_min: int
        Minimum frequency of a noun phrase occurrences in order to retrieve it. Default is 2.
    freq_max: int
        Maximum frequency of a noun phrase occurrences in order to retrieve it. Default is 10000.

    Examples
    --------
    >>> ents = _collect_entities(sample_corpus)
    >>> ents == {'swank-tank', 'prancercise', 'sassy unicorns', 'frank'}
    True
    """

    np_counts_total = {}
    docs_examined = 0
    for doc_id, doc_text in raw_corpus:
        if docs_examined > 0 and docs_examined % 1000 == 0:
            sorted_phrases = sorted(np_counts_total.items(),
                                    key=lambda item: -item[1])
            np_counts_total = dict(sorted_phrases)
            logging.info("at document #%i, considering %i phrases: %s..." %
                         (docs_examined, len(np_counts_total), sorted_phrases[0]))

        for np in TextBlob(doc_text).noun_phrases:
            np_counts_total[np] = np_counts_total.get(np, 0) + 1
        docs_examined += 1

    # Remove noun phrases in the list that have higher frequencies than 'freq_max' or lower frequencies than 'freq_min'
    np_counts = {}
    for np, count in np_counts_total.items():
        if freq_max >= count >= freq_min:
            np_counts[np] = count

    return set(np_counts)


def _tokenize_entities_document(text, entities, min_length=1, stopwords=None):
    '''
    A text tokenizer that passes only terms (a.k.a. 'entities') explicitly
    contained in the entities argument.

    Parameters
    ----------
    text : str
        A single text document to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> ents = _collect_entities(sample_corpus)
    >>> text = sample_corpus[0][1]
    >>> tokenized_text = _tokenize_entities_document(text,ents)
    >>> tokenized_text == [
    ...     u'frank', u'swank_tank', u'prancercise', u'sassy_unicorns']
    True
    '''
    result = []
    for np in TextBlob(text).noun_phrases:
        if np in entities:
            # filter out stop words
            tmp = "_".join(_simple_document(np, min_length=min_length, stopwords=stopwords))
            # if we end up with nothing, don't append an empty string
            if tmp:
                result.append(tmp)
    return result


def _tokenize_mixed_document(text, entities, min_length=1, stopwords=None):
    """
    A text tokenizer that retrieves entities ('noun phrases') first and simple words for the rest of the text.

    Parameters
    ----------
    text : str
        A single text document to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> ents = _collect_entities(sample_corpus)
    >>> text = sample_corpus[0][1]
    >>> tokenized_text = _tokenize_mixed_document(text,ents)
    >>> tokenized_text == [u'frank', u'swank_tank', u'sassy', u'unicorn',
    ... u'brony', u'prancercise', u'class', u'prancercise', u'popular',
    ... u'pastime', u'sassy_unicorns']
    True
    """
    result = []
    for np in TextBlob(text).noun_phrases:
        if ' ' in np and np not in entities:
            # break apart the noun phrase; it does not occur often enough in the collection of text to be considered.
            result.extend(_simple_document(np, min_length=min_length, stopwords=stopwords))
        else:
            # filter out stop words
            tmp = "_".join(_simple_document(np, min_length=min_length, stopwords=stopwords))
            # if we end up with nothing, don't append an empty string
            if tmp:
                result.append(tmp)
    return result


@register
def entities(corpus, min_length=1, freq_min=2, freq_max=10000, stopwords=None):
    """
    A tokenizer that extracts noun phrases from a corpus, then tokenizes all
    documents using those extracted phrases.

    Parameters
    ----------
    corpus : iterable of str
        A collection of text to be tokenized
    min_length : int
        Minimum length of any single word
    freq_min : int
        Minimum occurrence of phrase in order to be considered
    freq_max : int
        Maximum occurrence of phrase, beyond which it is ignored
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> tokenized_corpora = entities(sample_corpus)
    >>> next(tokenized_corpora) == ('doc1',
    ...     [u'frank', u'swank_tank', u'prancercise', u'sassy_unicorns'])
    True
    """
    # Tee in case it is a generator (else it will get exhausted).
    corpus_iterator = itertools.tee(corpus, 2)
    entities = _collect_entities(corpus_iterator[0], freq_min=freq_min, freq_max=freq_max)
    for doc_id, doc_text in corpus_iterator[1]:
        yield doc_id, _tokenize_entities_document(doc_text, entities, min_length=min_length,
                                       stopwords=stopwords)


@register
def mixed(corpus, min_length=1, freq_min=2, freq_max=10000, stopwords=None):
    """A text tokenizer that retrieves entities ('noun phrases') first and simple words for the rest of the text.

    Parameters
    ----------
    corpus : iterable of str
        A collection of text to be tokenized
    min_length : int
        Minimum length of any single word
    freq_min : int
        Minimum occurrence of phrase in order to be considered
    freq_max : int
        Maximum occurrence of phrase, beyond which it is ignored
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> tokenized_corpora = entities(sample_corpus)
    >>> next(tokenized_corpora) == ('doc1',
    ...     [u'frank', u'swank_tank', u'prancercise', u'sassy_unicorns'])
    True
    """
    corpus_iterators = itertools.tee(corpus, 2)
    entities = _collect_entities(corpus_iterators[0], freq_min=freq_min, freq_max=freq_max)
    for doc_id, doc_text in corpus_iterators[1]:
        yield doc_id, _tokenize_mixed_document(doc_text, entities,
                                                min_length=min_length,
                                                stopwords=stopwords)
