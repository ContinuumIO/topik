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
        -c, --field TEXT       the content field to extract text from, or for
                                folders, the field to store text as  [required]
        -f, --format TEXT      Data format provided: json_stream, folder_files,
                                large_json, elastic
        -m, --model TEXT       Statistical topic model: lda, plsa
        -o, --output TEXT      Topic modeling output path
        -t, --tokenizer TEXT   Tokenize method to use: simple, collocations,
                                entities, mix
        -n, --ntopics INTEGER  Number of topics to find
        --termite TEXT         Whether to output a termite plot as a result
        --ldavis TEXT          Whether to output an LDAvis-type plot as a result
        --help                 Show this message and exit.


To run this on our movie reviews data set:

.. code-block:: shell

   $ topik -d reviews -c text


The shell command is a front end to :func:`~.run_model`, which is also
accessible in python:

.. code-block:: python

   >>> from topik.simple_run.run import run_pipeline
   >>> run_pipeline("./reviews/", content_field="text")


Custom topic modeling flow
==========================

For interactive exploration and more efficient, involved workflows, there also
exists a Python API for using each part of the topic modeling workflow. There
are four phases to topic modeling with topik: data import,
tokenization/vectorization, modeling and visualization. Each phase is modular, with several
options available to you for each step.

An example complete workflow would be the following:

.. code-block:: python

   >>> from topik import read_input, tokenize, vectorize, run_model, visualize
   >>> raw_data = read_input("./reviews/")
   >>> content_field = "text"
   >>> raw_data = ((hash(item[content_field]), item[content_field]) for item in raw_data)
   >>> tokenized_corpus = tokenize(raw_data)
   >>> vectorized_corpus = vectorize(tokenized_corpus)
   >>> ntopics = 10
   >>> model = run_model(vectorized_corpus, ntopics=ntopics)
   >>> plot = visualize(model)
