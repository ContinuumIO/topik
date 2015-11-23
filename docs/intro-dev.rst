Development Guide
#################


Topik has been designed to be extensible at each of the five steps of topic
modeling:

  * data import
  * tokenization / transformation
  * vectorization
  * topic modeling
  * visualization


Each of these steps are designed using function registries to guide extension
development and to make creation of pluggable user interfaces feasible. The
general layout of topik is the following:


  * a folder (python package) for each step

    * __init__.py : exposes public API methods for the package.
    * _registry.py : implementation and instantiation of the function registry
      for each package. There is generally only one, but can be more than one
      registry per package. This file also contains the register decorator, used
      to register functions with the registry. This decorator runs when the file
      using it is imported.
    * ???_output.py : class implementation (possibly base class) of output from
      this package's step. This is not strictly necessary. When a step returns
      only an iterator of data, there is no additional output class created to
      wrap it.
    * any function implementations for the given step.
    * a tests folder, containing unit tests for the given step. These should not
      depend on output from other steps. Hard-code data as necessary.

External code can hook into the dictionary of registered methods using the
appropriate register decorator function, which should be made available in each
package's __init__.py. This decorator will execute when the foreign code is
first run, so make sure that you import your module before requesting the
dictionary of registered classes for a given step.

For general command line or IPython notebook usage, it is probably easier to
directly import functions from the folder structure, rather than depending on
the function registry. The registered dictionary approach makes dynamic UI
creation easier, but it hinders autocompletion. An intermediate approach would
be to assign the results of dictionary access to a variable before instantiating
the class. For example,


.. code-block:: python

   >>> # one-shot, but autocompletion of function arguments doesn't work
   >>> model = registered_models["LDA"](tokenized_corpora, 5)


.. code-block:: python

   >>> model_class = registered_models["LDA"]
   >>> # Autocompletion of class arguments should work here
   >>> model = model_class(tokenized_corpora, 5)

 
.. code-block:: python

   >>> # import model implementation directly:
   >>> from topik.models import lda
   >>> # Autocompletion of class arguments should work here
   >>> model = lda(vectorized_corpus, 5)
