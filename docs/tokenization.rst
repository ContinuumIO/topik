Tokenizing and Vectorizing
##########################

The next step in topic modeling is to break your documents up into individual
terms. This is called tokenization. Tokenization is done using the
:meth:`~.CorpusInterface.tokenize` method on a Corpus object
(returned from :func:`~.read_input`):

.. code-block:: python

   >>> tokenized_corpus = raw_data.tokenize()

Note on tokenize output
=======================

The :meth:`~.CorpusInterface.tokenize` method returns a new object, presently of
the :class:`~.DigestedDocumentCollection` type. Behind the scenes, the
:meth:`~.CorpusInterface.tokenize` method is storing the tokenized text
alongside your corpus, using whatever storage backend you have. This is an
in-place modification of that object. The new object serves two purposes:

  * It iterates over the particular tokenized representation of your corpus. You
    may have multiple tokenizations associated with a single corpus. The object
    returned from the tokenize function tracks the correct one.
  * It also performs vectorization on the fly, counting the number of words in
    each document, and returning a representation of each document as a bag of
    words (list of tuples, with each tuple being (word_id, word_count). This is
    generally the desired input to any topic model.

Make sure you assign this new object to a new variable. It is what you want to
feed into the topic modeling step.


Available methods
=================

The tokenize method accepts a few arguments to specify a tokenization method and
control behavior therein. The available tokenization methods are available in
the :data:`~.tokenizer_methods` dictionary. The presently available
methods are:

  * "simple": (default) lowercases input text and extracts single words. Uses
    Gensim.
  * "collocation": Collects bigrams and trigrams in addition to single words.
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
There are two steps to tokenization with collocation: establishing the patterns
of bigrams and trigrams, and subsequently tokenizing each document individually.

To obtain the bigram and trigram patterns, use the
:func:`~.collect_bigrams_and_trigrams` function:


.. code-block:: python

   >>> from topik.tokenizers import collect_bigrams_and_trigrams
   >>> patterns = collect_bigrams_and_trigrams(corpus)


Parameterization is done at this step, prior to tokenization of the corpus.  Tweakable parameters are:

  * top_n: limit results to a maximum number
  * min_length: the minimum length that any single word can be
  * min_bigram_freq: the minimum number of times a pair of words must occur together to be included
  * min_trigram_freq: the minimum number of times a triplet of words must occur together to be included


.. code-block:: python

   >>> patterns = collect_bigrams_and_trigrams(corpus, min_length=3, min_bigram_freq=3, min_trigram_freq=3)


For small bodies of text, you'll need small freq values, but this may be
correspondingly "noisy."

Next, feed the patterns into the :meth:`~.CorpusInterface.tokenize` method of
your corpus object:

.. code-block:: python

   >>> tokenized_corpus = raw_data.tokenize(method="collocation", patterns=patterns)
   


Entities tokenization
=====================

We refer to entities as noun phrases, as extracted by `the TextBlob library
<https://textblob.readthedocs.org/en/dev/>`_. Like collocation tokenization,
entities tokenization is a two-step process. First, you establish noun phrases
using the :func:`~.collect_entities` function:

.. code-block:: python

   >>> from topik.tokenizers import collect_entities
   >>> entities = collect_entities(corpus)


You can tweak noun phrase extraction with a minimum and maximum occurrence
frequency. This is the frequency across your entire corpus of documents.

.. code-block:: python

   >>> entities = collect_entities(corpus, freq_min=4, freq_max=10000)


Next, tokenize the document collection:


.. code-block:: python

   >>> tokenized_corpus = raw_data.tokenize(method="entities", entities=entities)


Mixed tokenization
==================

Mixed tokenization employs both the entities tokenizer and the simple tokenizer,
for when the entities tokenizer is overly restrictive, or for when words are
interesting both together and apart. Usage is similar to the entities tokenizer:

.. code-block:: python

   >>> from topik.tokenizers import collect_entities
   >>> entities = collect_entities(corpus)
   >>> tokenized_corpus = raw_data.tokenize(method="mixed", entities=entities)
