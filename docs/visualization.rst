Viewing results
===============

Each model supports a few standard outputs for examination of results:

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

   >>> from topik.visualizers.termite_plot import termite_html
   >>> termite = termite_html(model_output, "termite.html", "Termite Plot", topn=15)


.. raw:: html
   :file: viz/termite_open.html


.. raw:: html
   :file: viz/reviews_termite.html


.. code-block:: python

   >>> from topik.visualizers import lda_vis
   >>> lda_vis(model_output)


.. raw:: html
   :file: viz/ldavis_open.html

.. raw:: html
    :file: viz/reviews_pyldavis.html

