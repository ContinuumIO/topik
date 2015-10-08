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
Ng, Jordan (20003) <http://jmlr.csail.mit.edu/papers/v3/blei03a.html>`_, and
`Hoffman (1999) <http://www.cs.brown.edu/people/th/papers/Hofmann-UAI99.pdf>`_,
respectively.

Presently, all topic models require you to specify your desired number of topics
as input to the modeling process. With too many topics, you will overfit your
data, making your topics difficult to make sense of. With too few, you'll merge
topics together, which may hide important differences. Make sure you play with
the ntopics parameter to come up with the results that are best for your
collection of data.

To perform topic modeling on your tokenized data, select a model class from the
:data:`~.registered_models` dictionary, or simply import a model class
directly, and instantiate this object with your corpus and the number of topics
to model:

.. code-block:: python

   >>> from topik.models import registered_models, LDA
   >>> model = registered_models["LDA"](tokenized_data, 4)
   >>> model = LDA(tokenized_data, 4)


Presently, training the model is implicit in its instantiation. In other words,
when you create an object using the code above, the data are loaded into the
model, and the analysis to identify topics is performed immediately. That means
that instantiating an object may take some time. Progress indicators are on our
road map, but for now, please be patient and wait for your results.


Saving and loading results
==========================

The model object has a :meth:`~.TopicModelBase.save` method. This method saves a
JSON file that describes how to load the rest of the data for your model and for
your corpus. The :func:`~.load_model` function will read that JSON file, and
recreate the necessary corpus and model objects to leave you where you saved.
Each model has its own binary representation, and each corpus type has its own
storage backend. The JSON file saved here generally does not include corpus data
nor model data, but rather is simply instructions on where to find those data.
If you move files around on your hard disk, make sure to pick up everything with
the JSON file.

.. code-block:: python

   >>> model.save("test_data.json")
   >>> from topik.models import load_model
   >>> model = load_model("test_data.json")
   >>> model.get_top_words(10)
