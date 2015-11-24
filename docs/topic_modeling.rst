Topic modeling
##############

Topic modeling performs some mathematical modeling of your input data as a
(sparse) matrix of which documents contain which words, attempting to identify
latent "topics". At the end of modeling, each document will have a mix of topics
that it belongs to, each with a weight. Each topic in turn will have weights
associated with the collection of words from all documents.

Currently, Topik provides interfaces to or implements two topic modeling
algorithms, LDA (latent dirichlet allocation) and PLSA (probablistic latent
semantic analysis). LDA and PLSA are closely related, with LDA being a slightly
more recent development. The authoritative sources on LDA and PLSA are `Blei,
Ng, Jordan (2003) <http://jmlr.csail.mit.edu/papers/v3/blei03a.html>`_, and
`Hoffman (1999) <http://www.cs.brown.edu/people/th/papers/Hofmann-UAI99.pdf>`_,
respectively.

Presently, all topic models require you to specify your desired number of topics
as input to the modeling process. With too many topics, you will overfit your
data, making your topics difficult to make sense of. With too few, you'll merge
topics together, which may hide important differences. Make sure you play with
the ntopics parameter to come up with the results that are best for your
collection of data.

To perform topic modeling on your tokenized data, select a model function from the
:data:`topik.models.registered_models` dictionary, or simply import a model function directly,
and feed it your vectorized text.  Note that not all models are compatible with
all vectorizer methods.  In particular, LDA is not compatible with TF-IDF vectorization.

.. code-block:: python

   >>> from topik.models import registered_models, lda
   >>> model = registered_models["lda"](vectorized_corpora, 4)
   >>> model = LDA(vectorized_corpora, 4)

The output of modeling is a :class:`~.ModelOutput`.  This class provides simple methods
for obtaining the topic-term frequency and document-topic frequency, as well as some
supporting metadata.  This object is fed directly to visualization methods.
