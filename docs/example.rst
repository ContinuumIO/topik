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

    $ mkdir doc_example
    $ cd doc_example
    $ curl -o review_polarity.tar.gz http://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz
    $ tar -zxf review_polarity.tar.gz
    

Instead of using the dataset for `sentiment analysis
<https://en.wikipedia.org/wiki/Sentiment_analysis>`_, its initial purpose, we'll
perform `topic modeling <https://en.wikipedia.org/wiki/Topic_model>`_ on the
movie reviews. For that reason, we'll merge both folders `pos` and `neg`, to one
named `reviews`:

.. code-block:: shell

    $ mkdir reviews
    $ mv txt_sentoken/pos/* txt_sentoken/neg/* reviews/


High-level interface
====================

For quick, one-off studies, the command line interface allows you to specify
minimal information and obtain topic model plot output. For all available
options, please run ``topik --help``

.. code-block:: bash

    $ topik --help

    Usage: topik [OPTIONS]

      Run topic modeling

    Options:
      -d, --data TEXT        Path to input data for topic modeling  [required]
      -f, --format TEXT      Data format provided: json_stream, folder_files,
                             large_json, elastic, solr
      -m, --model TEXT       Statistical topic model: lda_batch, lda_online
      -o, --output TEXT      Topic modeling output path
      -t, --tokenizer TEXT   Tokenize method to use: simple, collocations,
                             entities, mix
      -n, --ntopics INTEGER  Number of topics to find
      --prefix_value TEXT    In 'large json' files, the prefix_value to extract
                             text from
      --event_value TEXT     In 'large json' files the event_value to extract text
                             from
      --field TEXT           In 'json stream' files, the field to extract text
                             from
      --help                 Show this message and exit.

To run this on our movie reviews data set:

.. code-block:: shell

   $ topik -d reviews

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
   >>> tokenized_corpus = raw_data.tokenize()
   >>> n_topics = 10
   >>> model = registered_models["LDA"](tokenized_corpus, n_topics)
   >>> from topik.viz import Termite
   >>> termite = Termite(model.termite_data(n_topics), "Termite Plot")
   >>> termite.plot('termite.html')
