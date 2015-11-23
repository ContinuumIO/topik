import itertools
import re

from topik.tokenizers.simple import _simple_document
from topik.tokenizers._registry import register

# sample_corpus for doctests
sample_corpus = [
            ("doc1", str(u"Frank the Swank-Tank walked his sassy unicorn, Brony,"
                         u" to prancercise class daily.  Prancercise was "
                         u"a tremendously popular pastime of sassy "
                         u"unicorns and retirees alike.")),
            ("doc2", str(u"Prancercise is a form of both art and fitniss, "
                         u"originally invented by sassy unicorns. It has "
                         u"recently been popularized by such retired "
                         u"celebrities as Frank The Swank-Tank."))]

# TODO: replace min_freqs with freq_bounds like ngrams takes.  Unify format across the board.
def _collect_bigrams_and_trigrams(raw_corpus, top_n=10000, min_length=1, min_freqs=None, stopwords=None):
    """collects bigrams and trigrams from collection of documents.  Input to collocation tokenizer.

    bigrams are pairs of words that recur in the collection; trigrams are triplets.

    Parameters
    ----------
    raw_corpus : iterable of tuple of (doc_id(str/int), doc_text(str))
        body of documents to examine
    top_n : int
        limit results to this many entries
    min_length : int
        Minimum length of any single word
    min_freqs : iterable of int
        threshold of when to consider a pair of words as a recognized n-gram,
        starting with bigrams.
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> patterns = _collect_bigrams_and_trigrams(sample_corpus, min_freqs=[2, 2])
    >>> patterns[0].pattern
    u'(frank swank|swank tank|sassy unicorns)'
    >>> patterns[1].pattern
    u'(frank swank tank)'
    """

    from nltk.collocations import TrigramCollocationFinder
    from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

    # generator of documents, turn each element to its list of words
    doc_texts = (_simple_document(doc_text, min_length=min_length, stopwords=stopwords)
                 for doc_id, doc_text in raw_corpus)
    # generator, concatenate (chain) all words into a single sequence, lazily
    words = itertools.chain.from_iterable(doc_texts)
    tcf = TrigramCollocationFinder.from_words(iter(words))

    bcf = tcf.bigram_finder()
    bcf.apply_freq_filter(min_freqs[0])
    bigrams = [' '.join(w) for w in bcf.nbest(BigramAssocMeasures.pmi, top_n)]

    tcf.apply_freq_filter(min_freqs[1])
    trigrams = [' '.join(w) for w in tcf.nbest(TrigramAssocMeasures.chi_sq, top_n)]

    bigrams_patterns = re.compile('(%s)' % '|'.join(bigrams), re.UNICODE)
    trigrams_patterns = re.compile('(%s)' % '|'.join(trigrams), re.UNICODE)

    return bigrams_patterns, trigrams_patterns


def _collocation_document(text, patterns, min_length=1, stopwords=None):
    """A text tokenizer that includes collocations(bigrams and trigrams).

    A collocation is sequence of words or terms that co-occur more often
    than would be expected by chance.  This function breaks a raw document
    up into tokens based on a pre-established collection of bigrams and
    trigrams.  This collection is derived from a body of many documents, and
    must be obtained in a prior step using the collect_bigrams_and_trigrams
    function.

    Uses nltk.collocations.TrigramCollocationFinder to
    find trigrams and bigrams.

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    patterns: tuple of compiled regex object to find n-grams
        Obtained from collect_bigrams_and_trigrams function
    min_length : int
        Minimum length of any single word
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> patterns = _collect_bigrams_and_trigrams(sample_corpus, min_freqs=[2, 2])
    >>> text = sample_corpus[0][1]
    >>> tokenized_text = _collocation_document(text,patterns)
    >>> tokenized_text == [
    ...     u'frank_swank', u'tank', u'walked', u'sassy', u'unicorn', u'brony',
    ...     u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
    ...     u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike']
    True
    """
    text = ' '.join(_simple_document(text, min_length=min_length, stopwords=stopwords))
    for pattern in patterns:
        text = re.sub(pattern, lambda match: match.group(0).replace(' ', '_'), text)
    return text.split()

@register
def ngrams(raw_corpus, min_length=1, freq_bounds=None, top_n=10000, stopwords=None):
    '''
    A tokenizer that extracts collocations (bigrams and trigrams) from a corpus
    according to the frequency bounds, then tokenizes all documents using those
    extracted phrases.

    Parameters
    ----------
    raw_corpus : iterable of tuple of (doc_id(str/int), doc_text(str))
        body of documents to examine
    min_length : int
        Minimum length of any single word
    freq_bounds : list of tuples of ints
        Currently ngrams supports bigrams and trigrams, so this list should
        contain two tuples (the first for bigrams, the second for trigrams),
        where each tuple consists of a (minimum, maximum) corpus-wide frequency.
    top_n : int
        limit results to this many entries
    stopwords: None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> tokenized_corpora = ngrams(sample_corpus, freq_bounds=[(2,100),(2,100)])
    >>> next(tokenized_corpora) == ('doc1',
    ...     [u'frank_swank', u'tank', u'walked', u'sassy', u'unicorn', u'brony',
    ...     u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
    ...     u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike'])
    True
    '''
    if not freq_bounds:
        freq_bounds=[(50, 10000), (20, 10000)]
    min_freqs = [freq[0] for freq in freq_bounds]
    patterns = _collect_bigrams_and_trigrams(raw_corpus, top_n=top_n, min_length=min_length, min_freqs=min_freqs,
                                 stopwords=stopwords)
    for doc_id, doc_text in raw_corpus:
        yield doc_id, _collocation_document(doc_text, patterns, min_length=min_length, stopwords=stopwords)
