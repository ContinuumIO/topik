Tokenizing
##########

The next step in topic modeling is to break your documents up into individual
terms. This is called tokenization. Tokenization is done using either the
:meth:`~.tokenize` dispatcher function on a Corpus iterator (returned from :func:`~.read_input`),
or using one of the tokenizer functions directly:

.. code-block:: python

   >>> tokenized_corpus = tokenize(raw_data)

Available methods
=================

The tokenize method accepts a few arguments to specify a tokenization method and
control behavior therein. The available tokenization methods are available in
the :data:`topik.tokenizers.registered_tokenizers` dictionary. The presently available
methods are:

  * "simple": (default) lowercases input text and extracts single words. Uses
    Gensim.
  * "ngrams": Collects bigrams and trigrams in addition to single words.
    Uses NLTK.
  * "entities": Extracts noun phrases as entities. Uses TextBlob.
  * "mixed": first extracts noun phrases as entities, then follows up with
    simple tokenization for single words. Uses TextBlob.

All methods accept a keyword argument ``stopwords``, which are words that will
be ignored in tokenization. These are words that add little content value, such
as prepositions. The default, ``None``, loads and uses gensim's STOPWORDS
collection.


Collocation tokenization
========================

Collocation tokenization collects phrases of words (pairs and triplets, bigrams
and trigrams) that occur together often throughout your collection of documents.

To obtain the bigram and trigram patterns, use the
:func:`~.ngrams` function:


.. code-block:: python

   >>> from topik.tokenizers import ngrams
   >>> tokens = ngrams(corpus, freq_bounds=[(5,10000), (3, 10000)])


Tweakable parameters are:

  * top_n: limit results to a maximum number
  * min_length: the minimum length that any single word can be
  * freq_bounds: list of tuples of [(min_freq, max_freq)].  Min_freq is the minimum number of
    times that a pair occurs before being considered.  The first entry in this list is bigrams.
    Presently, only bigrams and trigrams are supported.


For small bodies of text, you'll need small freq values, but this may be
correspondingly "noisy."


Entities tokenization
=====================

We refer to entities as noun phrases, as extracted by `the TextBlob library
<https://textblob.readthedocs.org/en/dev/>`_.  Topik provides the :func:`~topik.tokenizers.entities.entities`
function.

You can tweak noun phrase extraction with a minimum and maximum occurrence
frequency. This is the frequency across your entire corpus of documents.

.. code-block:: python

   >>> from topik.tokenizers import entities
   >>> tokens = entities(corpus, min_length=1, freq_min=4, freq_max=10000)


Mixed tokenization
==================

:func:`~topik.tokenizers.entities.mixed` tokenization employs both the entities tokenizer and the simple tokenizer,
for when the entities tokenizer is overly restrictive, or for when words are
interesting both together and apart. Usage is similar to the entities tokenizer:

.. code-block:: python

   >>> from topik.tokenizers import mixed
   >>> tokens = mixed(corpus, min_length=1, freq_min=4, freq_max=10000)
