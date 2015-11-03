import itertools
import re

from topik.tokenizers.simple import _simple_document
from ._registry import register

# imports used only for doctests
from topik.tests import test_data_path



def _collect_bigrams_and_trigrams(collection, top_n=10000, min_length=1, min_freqs=None, stopwords=None):
    """collects bigrams and trigrams from collection of documents.  Input to collocation tokenizer.

    bigrams are pairs of words that recur in the collection; trigrams are triplets.

    Parameters
    ----------
    collection : iterable of str
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
    >>> from topik.readers import read_input
    >>> raw_data = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> patterns = _collect_bigrams_and_trigrams(raw_data, min_freqs=[5, 3])
    >>> patterns[0]
    u'(free standing|ac electrodeposition|centered cubic|spatial resolution|vapor deposition\
|wear resistance|plastic deformation|electrical conductivity|field magnets|v o|\
transmission electron|x ray|et al|ray diffraction|electron microscopy|room \
temperature|diffraction xrd|electron microscope|results indicate|scanning \
electron|m s|doped zno|microscopy tem|polymer matrix|size distribution|mechanical \
properties|grain size|diameters nm|high spatial|particle size|high resolution|ni \
al|diameter nm|range nm|high field|high strength|c c)'
    >>> patterns[1]
    u'(differential scanning calorimetry|face centered cubic|ray microanalysis analytical|\
physical vapor deposition|transmission electron microscopy|x ray diffraction|microanalysis \
analytical electron|chemical vapor deposition|high aspect ratio|analytical electron \
microscope|ray diffraction xrd|x ray microanalysis|high spatial resolution|high \
field magnets|atomic force microscopy|electron microscopy tem|narrow size distribution\
|scanning electron microscopy|building high field|silicon oxide nanowires|particle size \
nm)'
    """

    from nltk.collocations import TrigramCollocationFinder
    from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

    # generator of documents, turn each element to its list of words
    documents = (_simple_document(text, min_length=min_length, stopwords=stopwords)
                 for text in collection.get_generator_without_id())
    # generator, concatenate (chain) all words into a single sequence, lazily
    words = itertools.chain.from_iterable(documents)
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
    >>> from topik.readers import read_input
    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> patterns = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=2, min_trigram_freq=2)
    >>> tokenized_data = raw_data.tokenize(method="collocation", patterns=patterns)
    >>> ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
    >>> solution_tokens = [u'transition_metal', u'oxides', u'considered', u'generation',
    ... u'materials', u'field', u'electronics', u'advanced', u'catalysts',
    ... u'tantalum', u'v_oxide', u'reports', u'synthesis_material',
    ... u'nanometer_size', u'unusual', u'properties', u'work_present',
    ... u'synthesis', u'ta', u'o', u'nanorods', u'sol', u'gel', u'method',
    ... u'dna', u'structure', u'directing', u'agent', u'size', u'nanorods',
    ... u'order', u'nm_diameter', u'microns', u'length', u'easy', u'method',
    ... u'useful', u'preparation', u'nanomaterials', u'electronics', u'biomedical',
    ... u'applications', u'catalysts']
    >>> solution_tokens in tokenized_texts
    True
    """
    text = ' '.join(_simple_document(text, min_length=min_length, stopwords=stopwords))
    for pattern in patterns:
        text = re.sub(pattern, lambda match: match.group(0).replace(' ', '_'), text)
    return text.split()

@register
def ngrams(corpus, min_length=1, freq_bounds=None, top_n=10000, stopwords=None):
    if not freq_bounds:
        freq_bounds=[(50, 10000), (20, 10000)]
    min_freqs = [freq[0] for freq in freq_bounds]
    patterns = _collect_bigrams_and_trigrams(corpus, top_n=top_n, min_length=min_length, min_freqs=min_freqs,
                                 min_trigram_freq=freq_bounds[1][0], stopwords=stopwords)
    for doc in corpus:
        yield _collocation_document(doc, patterns, min_length=min_length, stopwords=stopwords)
