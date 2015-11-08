import itertools
import re

from topik.tokenizers.simple import _simple_document
from topik.tokenizers._registry import register

# sample_corpus for doctests
sample_corpus = [
            ("doc1", str(u"Frank the Stank-Tank walked his sassy unicorn, Brony,"
                         u" to prancercise class daily.  Prancercise was "
                         u"a tremendously popular pastime of sassy "
                         u"unicorns and retirees alike.")),
            ("doc2", str(u"Prancercise is a form of both art and fitniss, "
                         u"originally invented by sassy unicorns. It has "
                         u"recently been popularized by such retired "
                         u"celebrities as Frank The Stank-Tank."))]

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
    u'(frank stank|stank tank|sassy unicorns)'
    >>> patterns[1].pattern
    u'(frank stank tank)'
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
    >>> text = sample_corpus[0][1]
    >>> #raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> #patterns = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=2, min_trigram_freq=2)
    >>> #tokenized_data = raw_data.tokenize(method="collocation", patterns=patterns)
    >>> #ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
    >> #solution_tokens = [u'transition_metal', u'oxides', u'considered', u'generation',
    ... u'materials', u'field', u'electronics', u'advanced', u'catalysts',
    ... u'tantalum', u'v_oxide', u'reports', u'synthesis_material',
    ... u'nanometer_size', u'unusual', u'properties', u'work_present',
    ... u'synthesis', u'ta', u'o', u'nanorods', u'sol', u'gel', u'method',
    ... u'dna', u'structure', u'directing', u'agent', u'size', u'nanorods',
    ... u'order', u'nm_diameter', u'microns', u'length', u'easy', u'method',
    ... u'useful', u'preparation', u'nanomaterials', u'electronics', u'biomedical',
    ... u'applications', u'catalysts']
    >> #solution_tokens in tokenized_texts
    True
    """
    text = ' '.join(_simple_document(text, min_length=min_length, stopwords=stopwords))
    for pattern in patterns:
        text = re.sub(pattern, lambda match: match.group(0).replace(' ', '_'), text)
    return text.split()

@register
def ngrams(raw_corpus, min_length=1, freq_bounds=None, top_n=10000, stopwords=None):
    if not freq_bounds:
        freq_bounds=[(50, 10000), (20, 10000)]
    min_freqs = [freq[0] for freq in freq_bounds]
    patterns = _collect_bigrams_and_trigrams(raw_corpus, top_n=top_n, min_length=min_length, min_freqs=min_freqs,
                                 stopwords=stopwords)
    for doc_id, doc_text in raw_corpus:
        yield doc_id, _collocation_document(doc_text, patterns, min_length=min_length, stopwords=stopwords)
