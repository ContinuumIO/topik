Introduction Tutorial
=====================

In this tutorial we will examine `topik` with a practical example: Topic
Modeling for Movie Reviews.

- The Movie Review Dataset
- Using the high-level interface :func:`run_topic_model`
- Creating your own custom topic modeling flow
- Analyzing the results


The Movie Review Dataset
------------------------

In this tutorial we are going to use the `Sentiment Polarity Dataset Version 2.0
<http://www.cs.cornell.edu/people/pabo/movie-review-data/>`_ from Bo Pang and
Lillian Lee. This dataset is distributed with `NLTK <http://www.nltk.org/>`_
with permission from the authors.

You can download the individual dataset from `NLTK
<http://www.nltk.org/nltk_data/packages/corpora/movie_reviews.zip>`_, or
download all of ntlk's dataset, running the following commands from the python
interpreter:

.. code-block:: python

   >>> import nltk
   >>> nltk.download()


For more information on the datasets and download options visit `NLTK data
<http://www.nltk.org/data.html>`_.

Instead of using the dataset for `sentiment analysis <https://en.wikipedia.org/wiki/Sentiment_analysis>`_, its initial purpose,
we'll perform `topic modeling <https://en.wikipedia.org/wiki/Topic_model>`_ on the movie reviews. For that reason, we'll
merge both folders `pos` and `neg`, to one named `reviews`:

.. code-block:: python



High-level interfaces
---------------------


For quick, one-off studies, the command line interface allows you to specify
minimal information and obtain topic model plot output.


Custom topic modeling flow
--------------------------


For interactive exploration and more efficient, involved workflows, there also
exists a Python API for using each part of the topic modeling workflow. There
are three phases to topic modeling with topik: data import,
tokenization/vectorization, and modeling. Each phase is modular, with several
options available to you for each step.


