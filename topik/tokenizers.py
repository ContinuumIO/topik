from __future__ import absolute_import, print_function

import itertools
import logging
import re

import gensim
from gensim.parsing.preprocessing import STOPWORDS
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from textblob import TextBlob

# imports used only for doctests
from topik.tests import test_data_path
from topik.readers import read_input


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.INFO)


def tokenize_simple(text, stopwords=STOPWORDS):
    """A text tokenizer that simply lowercases, matches alphabetic
    characters and removes stopwords.
    Uses gensim.utils.tokenize and gensim.parsing.preprocessing.STOPWORDS.

    Parameters
    ----------
    text: input text to be tokenized
    stopwords: words to ignore as noise

    >>> id_documents = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> id, doc_text = next(iter(id_documents))
    >>> doc_text == str(
    ... 'Transition metal oxides are being considered as the next generation '
    ... 'materials in field such as electronics and advanced catalysts; between'
    ... ' them is Tantalum (V) Oxide; however, there are few reports for the '
    ... 'synthesis of this material at the nanometer size which could have '
    ... 'unusual properties. Hence, in this work we present the synthesis of '
    ... 'Ta2O5 nanorods by sol gel method using DNA as structure directing '
    ... 'agent, the size of the nanorods was of the order of 40 to 100 nm in '
    ... 'diameter and several microns in length; this easy method can be useful'
    ... ' in the preparation of nanomaterials for electronics, biomedical '
    ... 'applications as well as catalysts.')
    True
    >>> tokens = tokenize_simple(doc_text)
    >>> tokens == [
    ... u'transition', u'metal', u'oxides', u'considered', u'generation',
    ... u'materials', u'field', u'electronics', u'advanced', u'catalysts',
    ... u'tantalum', u'v', u'oxide', u'reports', u'synthesis', u'material',
    ... u'nanometer', u'size', u'unusual', u'properties', u'work', u'present',
    ... u'synthesis', u'ta', u'o', u'nanorods', u'sol', u'gel', u'method',
    ... u'dna', u'structure', u'directing', u'agent', u'size', u'nanorods',
    ... u'order', u'nm', u'diameter', u'microns', u'length', u'easy', u'method',
    ... u'useful', u'preparation', u'nanomaterials', u'electronics',
    ... u'biomedical', u'applications', u'catalysts']
    True
    """
    return [word for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords]

def collocations(stream, top_n=10000, min_bigram_freq=50, min_trigram_freq=20):
    """Extract text collocations (bigrams and trigrams), from a stream of words.

    Parameters
    ----------
    stream: iterable object
        An iterable of words

    top_n: int
        Number of collocations to retrieve from the stream of words (order by decreasing frequency). Default is 10000

    min_bigram_freq: int
        Minimum frequency of a bigram in order to retrieve it. Default is 50.

    min_trigram_freq: int
        Minimum frequency of a trigram in order to retrieve it. Default is 20.

    """
    tcf = TrigramCollocationFinder.from_words(stream)

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


def collect_bigrams_and_trigrams(collection, top_n = 10000, min_bigram_freq=50,
                                 min_trigram_freq=20, stopwords=STOPWORDS):
    """collects bigrams and trigrams from collection of documents.  Input to collocation tokenizer.

    bigrams are pairs of words that recur in the collection.

    Parameters
    ----------
    collection: iterable data to examine
    top_n: limit results to this many entries
    min_bigram_freq: (integer) threshold of when to consider a pair of words as a recognized bigram
    min_trigram_freq: (integer) threshold of when to consider a triplet of words as a recognized trigram
    stopwords: (iterable) collection of words to ignore in the corpus

    >>> raw_data = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> bigrams, trigrams = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=5, min_trigram_freq=3)
    >>> bigrams.pattern == str(
    ... '(free standing|centered cubic|spatial resolution|vapor deposition|wear'
    ... ' resistance|plastic deformation|electrical conductivity|field magnets|'
    ... 'transmission electron|ray diffraction|electron microscopy|room '
    ... 'temperature|diffraction xrd|electron microscope|results indicate|'
    ... 'scanning electron|doped zno|microscopy tem|polymer matrix|size '
    ... 'distribution|mechanical properties|grain size|high spatial|particle '
    ... 'size|high resolution|high field|high strength)')
    True
    >>> trigrams.pattern == str(
    ... '(differential scanning calorimetry|face centered cubic|ray '
    ... 'microanalysis analytical|physical vapor deposition|transmission '
    ... 'electron microscopy|microanalysis analytical electron|chemical vapor '
    ... 'deposition|high aspect ratio|analytical electron microscope|ray '
    ... 'diffraction xrd|high spatial resolution|high field magnets|atomic '
    ... 'force microscopy|electron microscopy tem|narrow size distribution|'
    ... 'scanning electron microscopy|building high field|silicon oxide '
    ... 'nanowires)')
    True
    """
    # generator of documents, turn each element to its list of words
    documents = (_split_words(text, stopwords) for text in collection.get_generator_without_id())
    # generator, concatenate (chain) all words into a single sequence, lazily
    words = itertools.chain.from_iterable(documents)
    bigrams, trigrams = collocations(words, top_n=top_n,  min_bigram_freq=min_bigram_freq,
                                     min_trigram_freq=min_trigram_freq)
    return bigrams, trigrams

def _split_words(text, stopwords):
    """Split text into a list of single words. Ignore any token in the `stopwords` set.

    """
    return [word
            for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords and len(word) > 2]

def tokenize_collocation(text, bigrams, trigrams, stopwords=STOPWORDS):
    """A text tokenizer that includes collocations(bigrams and trigrams).

    A collocation is sequence of words or terms
    that co-occur more often than would be expected by chance.  Bigrams and trigrams must be found from the document
    collection a-priori.  Use the collect_bigrams_and_trigrams function to do so.

    Uses gensim.parsing.preprocessing.STOPWORDS to remove stopwords and nltk.collocations.TrigramCollocationFinder to
    find trigrams and bigrams.

    Parameters
    ----------
    reader: generator
        A generator that yields each of the documents to tokenize. (e.g. topik.readers.iter_document_json_stream)

    top_n: int
        Number of collocations to retrieve from the stream of words (order by decreasing frequency). Default is 10000

    min_bigram_freq: int
        Minimum frequency of a bigram in order to retrieve it. Default is 50.

    min_trigram_freq: int
        Minimum frequency of a trigram in order to retrieve it. Default is 20.


    >>> id_documents = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> bigrams, trigrams = collect_bigrams_and_trigrams(id_documents, min_bigram_freq=2, min_trigram_freq=2)
    >>> id, doc_text = next(iter(id_documents))
    >>> tokenized_text = tokenize_collocation(doc_text, bigrams, trigrams)
    >>> tokenized_text == [
    ... u'transition_metal', u'oxides', u'considered', u'generation',
    ... u'materials', u'field', u'electronics', u'advanced', u'catalysts',
    ... u'tantalum', u'oxide', u'reports', u'synthesis', u'material',
    ... u'nanometer_size', u'unusual', u'properties', u'work_present',
    ... u'synthesis', u'nanorods', u'sol', u'gel', u'method', u'dna',
    ... u'structure', u'directing', u'agent', u'size', u'nanorods', u'order',
    ... u'diameter', u'microns', u'length', u'easy', u'method', u'useful',
    ... u'preparation', u'nanomaterials', u'electronics', u'biomedical',
    ... u'applications', u'catalysts']
    True
    """
    text = ' '.join(_split_words(text, stopwords))
    text = re.sub(trigrams, lambda match: match.group(0).replace(' ', '_'), text)
    text = re.sub(bigrams, lambda match: match.group(0).replace(' ', '_'), text)
    return text.split()


def find_entities(document_stream, freq_min=2, freq_max=10000):
    """Return noun phrases from stream of documents.

    Parameters
    ----------
    document_stream: iterable object

    freq_min: int
        Minimum frequency of a noun phrase occurrences in order to retrieve it. Default is 2.

    freq_max: int
        Maximum frequency of a noun phrase occurrences in order to retrieve it. Default is 10000.

    """
    np_counts_total = {}
    docs_examined = 0
    for id, doc in document_stream:
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


def tokenize_entities(text, entities, stopwords=STOPWORDS):
    """A tokenizer that extracts noun phrases from text.

    Requires that you first establish entities

    Uses gensim.parsing.preprocessing.STOPWORDS. to remove stopwords and textblob.TextBlob().noun_phrases to find
    `noun_phrases`.

    Parameters
    ----------
    reader: generator
        A generator that yields each of the documents to tokenize. (e.g. topik.readers.iter_document_json_stream)

    freq_min: int
        Minimum frequency of a noun phrase occurrences in order to retrieve it. Default is 2.

    freq_max: int
        Maximum frequency of a noun phrase occurrences in order to retrieve it. Default is 10000.


    >> id_documents = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
    >> entities = find_entities(id_documents)
    >> print('entities: %r' % entities)
    >> len(entities)
    >> i = iter(id_documents)
    >> id, doc_text = next(i)
    >> doc_text
    >> tokenized_text = tokenize_entities(doc_text, entities)
    >> tokenized_text
    >> id, doc_text = next(i)
    >> doc_text
    >> tokenized_text = tokenize_entities(doc_text, entities)

        2015-02-04 17:18:55,618 : INFO : collecting entities from <generator object iter_document_json_stream at 0x10eaf0280>
        2015-02-04 17:18:55,618 : INFO : at document #0, considering 0 phrases: []...
        2015-02-04 17:18:57,363 : INFO : selected 563 entities: [u'simulation examples', u'comparison trials', u'vldb',
                                        u'intelligent optimization algorithm', u'study outcomes', u'ge', u'standard program modules',
                                        u'optimization activity', u'opposite context', u'direct victimization']...
    >> tokenized_text
        [[u'rapid_solution_phase_chemical_reduction_method', u'inert_gas_protection', u'stable_copper_nanoparticle_colloid',
          u'average_particle_size', u'narrow_size_distribution', u'synthesis_route', u'ascorbic_acid', u'natural_vitamin_c',
          u'vc', u'copper_salt_precursor', u'general_oxidation_process', u'newborn_nanoparticles', u'xrd', u'uv_vis', u'copper_nanoparticles',
          u'excellent_antioxidant_ability', u'ascorbic_acid']]

    """
    result = []
    for np in TextBlob(text).noun_phrases:
        if np not in entities:
            # only consider phrases detected in entities (with frequency parameters)
            continue
        token = '_'.join(part for part in gensim.utils.tokenize(np))
        if len(token) < 2 or token in stopwords:
            # ignore very short phrases and stop words
            continue
        result.append(token)
    return result


def tokenize_mixed(text, entities, stopwords=STOPWORDS):
    """A text tokenizer that retrieves entities ('noun phrases') first and simple words for the rest of the text.

    Parameters
    ----------
    reader: generator
        A generator that yields each of the documents to tokenize. (e.g. topik.readers.iter_document_json_stream)

    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> entities = find_entities(raw_data)
    >>> id, text = next(iter(raw_data))
    >>> tokenized_text = tokenize_mixed(text, entities)

    """
    result = []
    for np in TextBlob(text).noun_phrases:
        if ' ' in np and np not in entities:
            tokens = [word for word in gensim.utils.tokenize(np, lower=True) if word not in stopwords]
            result.extend(tokens)
        else:
            token = '_'.join(part for part in gensim.utils.tokenize(np) if len(part) > 2)
            if len(token) < 2 or token in stopwords:
                # ignore very short phrases and stop words
                continue
            result.append(token)
    return result


# Add additional methods here as necessary to expose them to outside consumers.
tokenizer_methods = {"simple": tokenize_simple,
                     "collocation": tokenize_collocation,
                     "entities": tokenize_entities,
                     "mixed": tokenize_mixed
                     }
