Vectorization
#############

Vectorization is the process of transforming words into numerical representation.  It
involves the accumulation of the aggregate vocabulary, mapping that vocabulary to
numeric identifiers, and finally, some arithmetic involving word counts in documents, and
potentially in the collection.

Bag of Words vectorization
==========================

Bag of words is simply a word count.  Words are collected from the tokenized input, assigned numeric
identifiers, and counted.

:func:`~topik.vectorizers.bag_of_words.bag_of_words` is the default method applied
by the :func:`~topik.vectorizers._registry.vectorize` function:

.. code-block:: python

    >>> from topik import vectorize
    >>> vector_output = vectorize(tokenized_corpus)

TF-IDF vectorization
====================

:func:`~topik.vectorizers.tfidf.tfidf` (Term-Frequency-Inverse-Document-Frequency) is a scheme that weights words based not only
on how much they occur in a single document, but also how much they occur across the entire corpus.
Words that occur many times in one document, but not much over the corpus are deemed to be more
important under this scheme.

NOTE: TF-IDF is NOT compatible with LDA models as Bag-Of-Words vectorization is a fundamental assumption of LDA.

.. code-block:: python

    >>> from topik import vectorize
    >>> vector_output = vectorize(tokenized_corpus, method="tfidf")


Vectorizer output
=================

Vectorization is the step at which conversion from text to numerical identifiers happens.  For this
reason, the output of the vectorizer is an object that contains both the vectorized corpus, and
a dictionary mapping the text tokens to their numeric identifiers.  This object is defined in
:class:`~.VectorizerOutput`.  These output objects are passed directly to modeling functions.

