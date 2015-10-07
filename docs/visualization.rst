Viewing results
===============

Each model supports a few standard outputs for examination of results:

  * List of top N words for each topic
  * Termite plots
  * LDAvis-based plots

Example syntax for these:

.. code-block:: python

   >>> model.get_top_words(topn=10)


.. code-block:: python

   >>> from topik.viz import Termite
   >>> termite = Termite(lda.termite_data(n_topics), "Termite Plot")
   >>> termite.plot(os.path.join(dir_path, 'termite.html'))

.. code-block:: python

   >>> from topik.viz import LDAvis
   >>> TODO: Reed to add docs on LDAvis plotting

Each model is free to implement its own additional outputs - check the class
members for what might be available.
