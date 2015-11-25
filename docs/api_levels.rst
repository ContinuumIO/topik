API Levels
##########

There are 3 API levels in the Topik design.  At the highest level, very few details
need to be provided by the user, but less room for customization exists.

Top-level API (basic, quick experiments)
========================================

Basic functions are provided as immediate children of the topik module:

.. code-block:: python

    >>> from topik import TopikProject, read_input, tokenize, vectorize, run_model

These provide defaults, and allow pass-through of any other arguments as keyword arguments.


Package structure
=================

This is likely the most useful API for Python power users.  Import functions directly from
their packages.  This will show you their complete list of available arguments, and give you
autocompletion of those arguments.

.. code-block:: python

    >>> from topik.vectorizers.tfidf import tfidf
    >>> from topik.models.plsa import plsa


Registered functions
====================

This API layer exists primarily for creating extensible GUIs.  All functions for each processing step
are registered with a Borg-pattern dictionary upon import.  This dictionary should be useful in
modularly exposing available functionality, simply by querying keys.  What is not (yet) implemented
is any sort of type hinting that would let you also create appropriate input widgets for all inputs.