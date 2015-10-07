.. Topik documentation master file, created by
   sphinx-quickstart on Mon Feb  9 16:24:14 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Topik's documentation!
#################################

`Topik` is a Topic Modeling toolkit.


What's a topic model?
---------------------

The following three definitions are a good introduction to topic modeling:

- A topic model is a type of statistical model for discovering the abstract "topics" that occur in a collection of
  documents [#]_.

- Topic models are a suite of algorithms that uncover the hidden thematic structure in document collections.
  These algorithms help us develop new ways to search, browse and summarize large archives of texts [#]_.

- Topic models provide a simple way to analyze large volumes of unlabeled text. A "topic" consists of a cluster
  of words that frequently occur together [#]_.


Yet Another Topic Modeling Library
----------------------------------

Some of you may be wondering why the world needs yet another topic modeling library. There are already great topic
modeling libraries out there, see `Useful Topic Modeling Resources`_. In fact `topik` is built on top of some of
them.

The aim of `topik` is to provide a full suite and high-level interface for anyone interested in applying topic modeling.
For that purpose, `topik` includes many utilities beyond statistical modeling algorithms and wraps all of its
features into an easy callable function and a command line interface.

`Topik`'s desired goals are the following:

- Provide a simple and full-featured pipeline, from text extraction to final results analysis and interactive
  visualizations.

- Integrate available topic modeling resources and features into one common interface, making it accessible to the
  beginner and/or non-technical user.

- Include pre-processing data wrappers into the pipeline.

- Provide useful analysis and visualizations on topic modeling results.

- Be an easy and beginner-friendly module to contribute to.


Getting Started
===============

To demonstrate the ease of a typical `topik` workflow, we'll provide two examples: using the command line
interface and using the method :func:`topik.run.run_model`.

- Using the command line interface

To get help you can always type ``topik --help``.

.. code-block:: bash

    $ topik --help

    Usage: topik [OPTIONS]

      Run topic modeling

    Options:
      -d, --data TEXT        Path to input data for topic modeling  [required]
      -f, --format TEXT      Data format provided: json_stream, folder_files,
                             large_json  [required]
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


The following example runs the default model LDA(batch) over a json stream, extracting the field `text` with simple
word tokenization.

.. code-block:: bash

    $ topik -d ./topik/tests/data/test-data-1.json -f json_stream -o ./test -n 3 --field text -t entities

- Using :func:``topik.run.run_model``

The same previous example using :func:`run_model` would be:

.. code-block:: python

   >>> from topik.run import run_topic_model
   >>> run_topic_model(data='./topik/tests/data/test-data-1.json', format='json_stream', n_topics=3, field='text', \
                       dir_path='./topic_model')


Contents
========

User Guide
``````````
.. toctree::

   installation
   example
   usage_python
   intro-dev


Reference Guide
```````````````

.. toctree::

   api


Useful Topic Modeling Resources
===============================

- `Topic modeling, David M. Blei <http://www.cs.princeton.edu/~blei/topicmodeling.html>`_

Python libraries
````````````````
- `Gensim <https://radimrehurek.com/gensim/>`_
- `Pattern <http://www.clips.ua.ac.be/pattern>`_
- `TextBlob <http://textblob.readthedocs.org/en/dev/>`_
- `NLTK <http://www.nltk.org/>`_

R libraries
```````````
- `lda <http://cran.r-project.org/web/packages/lda/>`_
- `LDAvis <https://github.com/cpsievert/LDAvis>`_

Other
`````
- `Ditop <http://ditop.hs8.de/>`_

Papers
``````
- `Probabilistic Topic Models by David M.Blei <http://www.cs.princeton.edu/~blei/papers/Blei2012.pdf>`_

License Agreement
-----------------

`topik` is distributed under the `BSD 3-Clause license <http://opensource.org/licenses/BSD-3-Clause>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Footnotes
=========

.. [#] http://en.wikipedia.org/wiki/Topic_model.
.. [#] http://www.cs.princeton.edu/~blei/topicmodeling.html
.. [#] http://mallet.cs.umass.edu/topics.php
