from __future__ import absolute_import, print_function

import itertools
import logging
import re

# imports used only for doctests
from topik.tests import test_data_path


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def tokenize_simple(text, min_length=1, stopwords=None):
    """A text tokenizer that simply lowercases, matches alphabetic
    characters and removes stopwords.

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords: None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> from topik.readers import read_input
    >>> id_documents = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> id, doc_text = next(iter(id_documents))
    >>> doc_text
    u'Transition metal oxides are being considered as the next generation \
materials in field such as electronics and advanced catalysts; between\
 them is Tantalum (V) Oxide; however, there are few reports for the \
synthesis of this material at the nanometer size which could have \
unusual properties. Hence, in this work we present the synthesis of \
Ta2O5 nanorods by sol gel method using DNA as structure directing \
agent, the size of the nanorods was of the order of 40 to 100 nm in \
diameter and several microns in length; this easy method can be useful\
 in the preparation of nanomaterials for electronics, biomedical \
applications as well as catalysts.'
    >>> tokens = tokenize_simple(doc_text)
    >>> tokens
    [u'transition', u'metal', u'oxides', u'considered', \
u'generation', u'materials', u'field', u'electronics', \
u'advanced', u'catalysts', u'tantalum', u'v', u'oxide', \
u'reports', u'synthesis', u'material', u'nanometer', u'size', \
u'unusual', u'properties', u'work', u'present', u'synthesis', \
u'ta', u'o', u'nanorods', u'sol', u'gel', u'method', u'dna', \
u'structure', u'directing', u'agent', u'size', u'nanorods', \
u'order', u'nm', u'diameter', u'microns', u'length', u'easy', \
u'method', u'useful', u'preparation', u'nanomaterials', u'electronics', \
u'biomedical', u'applications', u'catalysts']
    """

    import gensim
    if not stopwords:
        from gensim.parsing.preprocessing import STOPWORDS as stopwords
    return [word for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords and len(word) >= min_length]


def collect_bigrams_and_trigrams(collection, top_n=10000, min_length=1, min_bigram_freq=50,
                                 min_trigram_freq=20, stopwords=None):
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
    min_bigram_freq : int
        threshold of when to consider a pair of words as a recognized bigram
    min_trigram_freq : int
        threshold of when to consider a triplet of words as a recognized trigram
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> from topik.readers import read_input
    >>> raw_data = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> bigrams, trigrams = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=5, min_trigram_freq=3)
    >>> bigrams.pattern
    u'(free standing|ac electrodeposition|centered cubic|spatial resolution|vapor deposition\
|wear resistance|plastic deformation|electrical conductivity|field magnets|v o|\
transmission electron|x ray|et al|ray diffraction|electron microscopy|room \
temperature|diffraction xrd|electron microscope|results indicate|scanning \
electron|m s|doped zno|microscopy tem|polymer matrix|size distribution|mechanical \
properties|grain size|diameters nm|high spatial|particle size|high resolution|ni \
al|diameter nm|range nm|high field|high strength|c c)'
    >>> trigrams.pattern
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
    documents = (tokenize_simple(text, min_length=min_length, stopwords=stopwords)
                 for text in collection.get_generator_without_id())
    # generator, concatenate (chain) all words into a single sequence, lazily
    words = itertools.chain.from_iterable(documents)
    tcf = TrigramCollocationFinder.from_words(iter(words))

    tcf.apply_freq_filter(min_trigram_freq)
    trigrams = [' '.join(w) for w in tcf.nbest(TrigramAssocMeasures.chi_sq, top_n)]
    logging.info("%i trigrams found: %s..." % (len(trigrams), trigrams[:20]))

    bcf = tcf.bigram_finder()
    bcf.apply_freq_filter(min_bigram_freq)
    bigrams = [' '.join(w) for w in bcf.nbest(BigramAssocMeasures.pmi, top_n)]
    logging.info("%i bigrams found: %s..." % (len(bigrams), bigrams[:20]))

    bigrams_patterns = re.compile('(%s)' % '|'.join(bigrams), re.UNICODE)
    trigrams_patterns = re.compile('(%s)' % '|'.join(trigrams), re.UNICODE)

    return bigrams_patterns, trigrams_patterns


def tokenize_collocation(text, patterns, min_length=1, stopwords=None):
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
    >>> id_documents = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> patterns = collect_bigrams_and_trigrams(id_documents, min_bigram_freq=2, min_trigram_freq=2)
    >>> id, doc_text = next(iter(id_documents))
    >>> tokenized_text = tokenize_collocation(doc_text, patterns)
    >>> tokenized_text
    [u'transition_metal', u'oxides', u'considered', u'generation', \
u'materials', u'field', u'electronics', u'advanced', u'catalysts', \
u'tantalum', u'v_oxide', u'reports', u'synthesis_material', \
u'nanometer_size', u'unusual', u'properties', u'work_present', \
u'synthesis', u'ta', u'o', u'nanorods', u'sol', u'gel', u'method', \
u'dna', u'structure', u'directing', u'agent', u'size', u'nanorods', \
u'order', u'nm_diameter', u'microns', u'length', u'easy', u'method', \
u'useful', u'preparation', u'nanomaterials', u'electronics', u'biomedical', \
u'applications', u'catalysts']
    """
    text = ' '.join(tokenize_simple(text, min_length=min_length, stopwords=stopwords))
    for pattern in patterns:
        text = re.sub(pattern, lambda match: match.group(0).replace(' ', '_'), text)
    return text.split()


def collect_entities(collection, freq_min=2, freq_max=10000):
    """Return noun phrases from collection of documents.

    Parameters
    ----------
    collection: Corpus-base derived object or iterable collection of raw text
    freq_min: int
        Minimum frequency of a noun phrase occurrences in order to retrieve it. Default is 2.
    freq_max: int
        Maximum frequency of a noun phrase occurrences in order to retrieve it. Default is 10000.

    """

    from textblob import TextBlob

    np_counts_total = {}
    docs_examined = 0
    for doc in collection.get_generator_without_id():
        if docs_examined > 0 and docs_examined % 1000 == 0:
            sorted_phrases = sorted(np_counts_total.items(),
                                    key=lambda item: -item[1])
            np_counts_total = dict(sorted_phrases)
            logging.info("at document #%i, considering %i phrases: %s..." %
                         (docs_examined, len(np_counts_total), sorted_phrases[0]))

        for np in TextBlob(doc).noun_phrases:
            np_counts_total[np] = np_counts_total.get(np, 0) + 1
        docs_examined += 1

    # Remove noun phrases in the list that have higher frequencies than 'freq_max' or lower frequencies than 'freq_min'
    np_counts = {}
    for np, count in np_counts_total.items():
        if freq_max >= count >= freq_min:
            np_counts[np] = count

    return set(np_counts)


def tokenize_entities(text, entities, min_length=1, stopwords=None):
    """A tokenizer that extracts noun phrases from text.

    Requires that you first establish entities using the collect_entities function

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> from topik.readers import read_input
    >>> id_documents = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
    >>> entities = collect_entities(id_documents)
    >>> len(entities)
    220
    >>> i = iter(id_documents)
    >>> _, doc_text = next(i)
    >>> doc_text
    u'Transition metal oxides are being considered as the next generation \
materials in field such as electronics and advanced catalysts; between\
 them is Tantalum (V) Oxide; however, there are few reports for the \
synthesis of this material at the nanometer size which could have \
unusual properties. Hence, in this work we present the synthesis of \
Ta2O5 nanorods by sol gel method using DNA as structure directing \
agent, the size of the nanorods was of the order of 40 to 100 nm in \
diameter and several microns in length; this easy method can be useful\
 in the preparation of nanomaterials for electronics, biomedical \
applications as well as catalysts.'
    >>> tokenized_text = tokenize_entities(doc_text, entities)
    >>> tokenized_text
    [u'transition']

    """
    from textblob import TextBlob
    result = []
    for np in TextBlob(text).noun_phrases:
        if np in entities:
            # filter out stop words
            tmp = "_".join(tokenize_simple(np, min_length=min_length, stopwords=stopwords))
            # if we end up with nothing, don't append an empty string
            if tmp:
                result.append(tmp)
    return result



def tokenize_mixed(text, entities, min_length=1, stopwords=None):
    """A text tokenizer that retrieves entities ('noun phrases') first and simple words for the rest of the text.

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords: None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> from topik.readers import read_input
    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> entities = collect_entities(raw_data)
    >>> id, text = next(iter(raw_data))
    >>> tokenized_text = tokenize_mixed(text, entities, min_length=3)
    >>> tokenized_text
    [u'transition', u'metal', u'oxides', u'generation', u'materials', u'tantalum', \
u'oxide', u'nanometer', u'size', u'unusual', u'properties', u'sol', u'gel', \
u'method', u'dna', u'easy', u'method', u'biomedical', u'applications']

    """
    from textblob import TextBlob
    result = []
    for np in TextBlob(text).noun_phrases:
        if ' ' in np and np not in entities:
            # break apart the noun phrase; it does not occur often enough in the collection of text to be considered.
            result.extend(tokenize_simple(np, min_length=min_length, stopwords=stopwords))
        else:
            # filter out stop words
            tmp = "_".join(tokenize_simple(np, min_length=min_length, stopwords=stopwords))
            # if we end up with nothing, don't append an empty string
            if tmp:
                result.append(tmp)
    return result


# Add additional methods here as necessary to expose them to outside consumers.
tokenizer_methods = {"simple": tokenize_simple,
                     "collocation": tokenize_collocation,
                     "entities": tokenize_entities,
                     "mixed": tokenize_mixed
                     }
