Introduction Tutorial
=====================

In this tutorial we will examine `topik` with a practical example: Topic Modeling for Movie Reviews.

- The Movie Review Dataset
- Using the high-level interface ``run_topic_model``
- Creating your own custom topic modeling flow
- Analyzing the results


The Movie Review Dataset
------------------------

In this tutorial we are going to use the `Sentiment Polarity Dataset Version 2.0
<http://www.cs.cornell.edu/people/pabo/movie-review-data/>`_ from Bo Pang and Lillian Lee. This dataset is distributed
with `NLTK <http://www.nltk.org/>`_ with permission from the authors.

You can download the individual dataset from `NLTK <http://www.nltk.org/nltk_data/packages/corpora/movie_reviews.zip>`_,
or download all of ntlk's dataset, running the following commands from the python interpreter:

.. code-block:: python
    >>> import nltk
    >>> nltk.download()


For more information on the datasets and download options visit `NLTK data <http://www.nltk.org/data.html>`_.

Instead of using the dataset in for `sentiment analysis`, its initial purpose, we'll perform `topic modeling` on the
movie reviews. For that reason, we'll merge both folders `pos` and `neg`, to one named `reviews`.


High-level interfaces
---------------------

As mentioned in the introduction page, there a two high-level interfaces: the command-line interface and the function
topik.run()

Custom topic modeling flow
--------------------------




Analyzing the results
---------------------
