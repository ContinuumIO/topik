from __future__ import absolute_import, print_function

import logging
import itertools
import re

from textblob import TextBlob
import gensim
from gensim.parsing.preprocessing import STOPWORDS

from topik.utils import collocations, entities

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
                    '{}/test-data-1.json',
                    content_field="text")
    >>> id, doc_text = next(iter(id_documents))
    >>> doc_text
    "'Interstellar' was incredible.  The visuals, the score, the acting,
    were all amazing.  The plot is definitely on of the most original I've
    seen in a while."
    >>> tokens = tokenize_simple(doc_text)
    >>> head(simple_tokenizer)
        [['interstellar', 'incredible', 'visuals', 'score', 'acting',
          'amazing', 'plot', 'definitely', 'original', 've', 'seen']]
    """.format(test_data_path)
    return [word for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords]



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
                    '{}/test-data-1.json',
                    content_field="text")
    >>> bigrams, trigrams = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=5, min_trigram_freq=3)
    >>> bigrams
    ["steve"]
    >>> trigrams
    ["frank"]
    """.format(test_data_path)
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


    >>> raw_data = read_input('{}/test-data-2.json', content_field="abstract")
    >>> bigrams, trigrams = collect_bigrams_and_trigrams(raw_data, min_bigram_freq=2, min_trigram_freq=2)
    >>> tokenized_text = tokenize_collocation(next(iter(raw_data)), bigrams, trigrams)
    ['paper', 'simple', 'rapid', 'solution', 'phase', 'chemical',
     'reduction', 'method', 'inert', 'gas', 'protection',
     'preparing', 'stable', 'copper', 'nanoparticle', 'colloid',
     'average', 'particle', 'size', 'narrow', 'size_distribution',
     'synthesis_route', 'ascorbic_acid', 'natural', 'vitamin',
     'serves', 'reducing', 'agent', 'antioxidant', 'reduce',
     'copper', 'salt', 'precursor', 'effectively', 'prevent',
     'general', 'oxidation', 'process', 'occurring', 'newborn',
     'nanoparticles', 'xrd', 'vis', 'confirm', 'formation', 'pure',
     'face', 'centered', 'cubic', 'fcc', 'copper', 'nanoparticles',
     'excellent', 'antioxidant', 'ability', 'ascorbic_acid']

    """.format(test_data_path)
    text = ' '.join(_split_words(text, stopwords))
    text = re.sub(trigrams, lambda match: match.group(0).replace(' ', '_'), text)
    text = re.sub(bigrams, lambda match: match.group(0).replace(' ', '_'), text)
    return text.split()


def find_entities(collection, freq_min=2, freq_max=10000):
        return entities(collection, freq_max=freq_max, freq_min=freq_min)

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


    >>> id_documents = iter_document_json_stream('{}/test-data-2.json', "abstract")
    >>> ids, doc_text = unzip(id_documents)
    >>> collocation_tokenizer = EntitiesTokenizer(doc_text, 1)
        2015-02-04 17:18:55,618 : INFO : collecting entities from <generator object iter_document_json_stream at 0x10eaf0280>
        2015-02-04 17:18:55,618 : INFO : at document #0, considering 0 phrases: []...
        2015-02-04 17:18:57,363 : INFO : selected 563 entities: [u'simulation examples', u'comparison trials', u'vldb',
                                        u'intelligent optimization algorithm', u'study outcomes', u'ge', u'standard program modules',
                                        u'optimization activity', u'opposite context', u'direct victimization']...
    >>> head(collocation_tokenizer)
        [[u'rapid_solution_phase_chemical_reduction_method', u'inert_gas_protection', u'stable_copper_nanoparticle_colloid',
          u'average_particle_size', u'narrow_size_distribution', u'synthesis_route', u'ascorbic_acid', u'natural_vitamin_c',
          u'vc', u'copper_salt_precursor', u'general_oxidation_process', u'newborn_nanoparticles', u'xrd', u'uv_vis', u'copper_nanoparticles',
          u'excellent_antioxidant_ability', u'ascorbic_acid']]

    """.format(test_data_path)
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

    >>> raw_data = read_input('{}/test-data-2.json', content_field="abstract")
    >>> entities = find_entities(raw_data)
    >>> id, text = next(iter(raw_data))
    >>> tokenized_text = tokenize_mixed(text, entities)

    """.format(test_data_path)
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
