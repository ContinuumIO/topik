from __future__ import absolute_import

import logging
import itertools
import re

from textblob import TextBlob
import gensim
from gensim.parsing.preprocessing import STOPWORDS

from topik.readers import iter_document_json_stream, head
from topik.utils import collocations, entities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class SimpleTokenizer(object):
    """A text tokenizer that simply lowercases, matches alphabetic characters and removes stopwords.
    Uses gensim.utils.tokenize and gensim.parsing.preprocessing.STOPWORDS.

    Parameters
    ----------
    reader: generator
        A generator that yields each of the documents to tokenize. (e.g. topik.readers.iter_document_json_stream)

    >>> doc_text = iter_document_json_stream('./topik/tests/data/test-data-1', "text")
    >>> head(doc_text)
        [u"'Interstellar' was incredible. The visuals, the score, the acting, were all amazing. The plot is definitely one
            of the most original I've seen in a while."]
    >>> simple_tokenizer = SimpleTokenizer(doc_text)
    >>> head(simple_tokenizer)
        [[u'interstellar', u'incredible', u'visuals', u'score', u'acting', u'amazing', u'plot', u'definitely',
            u'original', u've', u'seen']]

    """
    def __init__(self, reader):
        self.reader = reader

    def __iter__(self):
        for text in self.reader:
            # tokenize each message; simply lowercase & match alphabetic chars
            tokenized_text = self.tokenize(text)
            yield tokenized_text

    def tokenize(self, text, stopwords=STOPWORDS):
        """
        Split text into a list of single words. Ignore any token in the `stopwords` set.

        """
        return [word for word in gensim.utils.tokenize(text, lower=True)
                if word not in STOPWORDS]


class CollocationsTokenizer(object):
    """A text tokenizer that includes collocations(bigrams and trigrams). A collocation is sequence of words or terms
    that co-occur more often than would be expected by chance.

    Uses gensim.parsing.preprocessing.STOPWORDS. to remove stopwords and nltk.collocations.TrigramCollocationFinder to
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


    >>> doc_text = iter_document_json_stream('./topik/tests/data/test-data-2', "abstract")
    >>> collocation_tokenizer = CollocationsTokenizer(doc_text, min_bigram_freq=2, min_trigram_freq=2)
        2015-02-03 16:36:55,758 : INFO : collecting bigrams and trigrams from <generator object iter_document_json_stream at 0x10e8ad5f0>
        2015-02-03 16:36:55,778 : INFO : 43 trigrams found: [u'posttraumatic stress disorder', u'likely correctly identify'...]
        2015-02-03 16:36:55,780 : INFO : 127 bigrams found: [u'act directed', u'ascorbic acid', u'features objects'...]
    >>> head(collocation_tokenizer)
        [[u'paper', u'simple', u'rapid', u'solution', u'phase', u'chemical', u'reduction', u'method', u'inert', u'gas',
        u'protection', u'preparing', u'stable', u'copper', u'nanoparticle', u'colloid', u'average', u'particle',
        u'size', u'narrow', u'size_distribution', u'synthesis_route', u'ascorbic_acid'...]

    """
    def __init__(self, reader, top_n = 10000, min_bigram_freq=50, min_trigram_freq=20):
        self.reader = reader
        self.iter_1, self.iter_2 = itertools.tee(self.reader, 2)
        self.min_bigram_freq = min_bigram_freq
        self.min_trigram_freq = min_trigram_freq
        self.top_n = top_n
        logging.info("collecting bigrams and trigrams from %s" % self.iter_1)
        # generator of documents, turn each element to its list of words
        documents = (self.split_words(text) for text in self.iter_1)
        # generator, concatenate (chain) all words into a single sequence, lazily
        words = itertools.chain.from_iterable(documents)
        self.bigrams, self.trigrams = collocations(words, top_n=self.top_n,  min_bigram_freq=self.min_bigram_freq,
                                                   min_trigram_freq=self.min_trigram_freq)

    def split_words(self, text, stopwords=STOPWORDS):
        """Split text into a list of single words. Ignore any token in the `stopwords` set.

        """
        return [word
                for word in gensim.utils.tokenize(text, lower=True)
                if word not in STOPWORDS and len(word) > 2]

    def tokenize(self, message):
        """Break text (string) into a list of Unicode tokens.

        The resulting tokens include found collocations.

        """
        text = u' '.join(self.split_words(message))
        text = re.sub(self.trigrams, lambda match: match.group(0).replace(u' ', u'_'), text)
        text = re.sub(self.bigrams, lambda match: match.group(0).replace(u' ', u'_'), text)
        return text.split()

    def __iter__(self):
        for message in self.iter_2:
            yield self.tokenize(message)



class EntitiesTokenizer(object):
    """A tokenizer that extracts noun phrases from text.

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


    >>> doc_text = iter_document_json_stream('./topik/tests/data/test-data-2', "abstract")
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

    """
    def __init__(self, reader, freq_min=2, freq_max=10000):
        self.reader = reader
        self.iter_1, self.iter_2 = itertools.tee(self.reader, 2)
        logging.info("collecting entities from %s" % self.reader)
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.entities = entities(self.iter_1, freq_max=self.freq_max, freq_min=self.freq_min)
        logging.info("selected %i entities: %s..." %
                     (len(self.entities), list(self.entities)[:10]))

    def __iter__(self):
        for message in self.iter_2:
            yield self.tokenize(message)

    def tokenize(self, message, stopwords=STOPWORDS):
        """Split text (string) into a list of tokens.
        The resulting tokens can be longer phrases, e.g. `material_sciences`, `artificial_intelligence`, etc.

        """
        result = []
        for np in TextBlob(message).noun_phrases:
            if np not in self.entities:
                # only consider phrases detected in entities (with frequency parameters)
                continue
            token = u'_'.join(part for part in gensim.utils.tokenize(np))
            if len(token) < 2 or token in stopwords:
                # ignore very short phrases and stop words
                continue
            result.append(token)
        return result


class MixedTokenizer(object):
    """A text tokenizer that retrieves entities ('noun phrases') first and simple words for the rest of the text.

    Parameters
    ----------
    reader: generator
        A generator that yields each of the documents to tokenize. (e.g. topik.readers.iter_document_json_stream)

    >>> doc_text = iter_document_json_stream('./topik/tests/data/test-data-2', "abstract")
    >>> mixed_tokenizer = MixedTokenizer(doc_text)

    >>> head(mixed_tokenizer)

    """
    def __init__(self, reader):
        self.reader = reader
        self.iter_1, self.iter_2 = itertools.tee(self.reader, 2)
        logging.info("collecting entities from %s" % self.iter_1)
        self.entities = entities(self.iter_1)
        logging.info("selected %i entities: %s..." %
                     (len(self.entities), list(self.entities)[:10]))

    def __iter__(self):
        for message in self.iter_2:
            yield self.tokenize(message)

    def tokenize(self, message, stopwords=STOPWORDS):
        """Split text (string) into a list of Unicode tokens.

        The resulting tokens can be longer phrases, e.g. `material_sciences`, `artificial_intelligence`, etc.

        """
        result = []
        for np in TextBlob(message).noun_phrases:
            if u' ' in np and np not in self.entities:
                tokens = [word for word in gensim.utils.tokenize(np, lower=True) if word not in STOPWORDS]
                result.extend(tokens)
            else:
                token = u'_'.join(part for part in gensim.utils.tokenize(np) if len(part) > 2)
                if len(token) < 2 or token in stopwords:
                    # ignore very short phrases and stop words
                    continue
                result.append(token)
        return result
