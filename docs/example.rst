Introduction Tutorial
#####################

In this tutorial we will examine `topik` with a practical example: Topic
Modeling for Movie Reviews.


Preparing The Movie Review Dataset
==================================

In this tutorial we are going to use the `Sentiment Polarity Dataset Version 2.0
<http://www.cs.cornell.edu/people/pabo/movie-review-data/>`_ from Bo Pang and
Lillian Lee.

.. code-block:: shell

    $ curl http://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz
    $ tar -zxf review_polarity.tar.gz
    

Instead of using the dataset for `sentiment analysis
<https://en.wikipedia.org/wiki/Sentiment_analysis>`_, its initial purpose, we'll
perform `topic modeling <https://en.wikipedia.org/wiki/Topic_model>`_ on the
movie reviews. For that reason, we'll merge both folders `pos` and `neg`, to one
named `reviews`:

.. code-block:: shell

    $ mkdir reviews
    $ mv review_polarity/txt_sentoken/pos/* review_polarity/txt_sentoken/neg/* reviews/


High-level interface
====================

For quick, one-off studies, the command line interface allows you to specify
minimal information and obtain topic model plot output. For all available
options, please run ``topik --help``

.. code-block:: shell

   $ topik --help
   $ topik reviews

The shell command is a front end to :func:`~.run_model`, which is also
accessible in python:

.. code-block:: python

   >>> from topik.run import run_model
   >>> run_model("reviews")


Custom topic modeling flow
==========================

For interactive exploration and more efficient, involved workflows, there also
exists a Python API for using each part of the topic modeling workflow. There
are four phases to topic modeling with topik: data import,
tokenization/vectorization, modeling and visualization. Each phase is modular, with several
options available to you for each step.

An example complete workflow would be the following:

.. code-block:: python

   >>> from topik import read_input, registered_models
   >>> raw_data = read_input("reviews")
   >>> raw_data.tokenize()
   >>> n_topics = 10
   >>> model = registered_models["LDA"](raw_data, n_topics)
   >>> from topik.viz import Termite
   >>> termite = Termite(model.termite_data(n_topics), "Termite Plot")
   >>> termite.plot('termite.html')
