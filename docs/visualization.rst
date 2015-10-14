Viewing results
===============

Each model supports a few standard outputs for examination of results:

  * List of top N words for each topic
  * Termite plots
  * LDAvis-based plots

    * topik's LDAvis-based plots use the pyLDAvis module, which is itself a
    Python port of the R_ldavis library.  The visualization consists of two
    linked, interactive views.  On the left is a projection of the topics onto
    a 2-dimensional space, where the area of each circle represents that topic's
    relative prevalence in the corpus.  The view on the right shows details of
    the composition of the topic (if any) selected in the left view.  The slider
    at the top of the right view adjusts the relevance metric used when ranking
    the words in a topic.  A value of 1 on the slider will rank terms by their
    probabilities for that topic (the red bar), whereas a value of 0 will rank
    them by their probabilities for that topic divided by their probabilities for the overall corpus (red divided by blue).

Example syntax for these:

.. code-block:: python

   >>> model.get_top_words(topn=10)


.. code-block:: python

   >>> from topik.viz import Termite
   >>> termite = Termite(lda.termite_data(n_topics), "Termite Plot")
   >>> termite.plot(os.path.join(dir_path, 'termite.html'))

.. code-block:: python

   >>> from topik.viz import LDAvis
   >>> raw_data = read_input("reviews", content_field=None)
   >>> tokenized_corpus = raw_data.tokenize()
   >>> n_topics = 10
   >>> model = registered_models["LDA"](tokenized_corpus, n_topics)
   >>> from topik.viz import plot_lda_vis
   >>> plot_lda_vis(model.to_py_lda_vis())

.. raw:: html
    :file: viz/reviews_pyldavis.html

Each model is free to implement its own additional outputs - check the class
members for what might be available.

.. include:: <viz/reviews_pyldavis.html>
    :code: html
