Development Guide
#################


Topik has been designed to be extensible at each of the four steps of topic modeling:

  * data import
  * tokenization / vectorization
  * topic modeling
  * visualization


Each of these steps are designed using abstract interfaces to guide extension
development and to make creation of pluggable user interfaces feasible.  The
general layout of topik is the following:


  * __init__.py imports registered class dictionaries and functions from each
    folder
  * a folder (python package) for each step

    * base???.py

      * abstract interface to be implemented by any concrete classes
      * register function that is used as a decorator to register classes
      * dictionary of registered classes for this step (global variable)

    * any concrete implementations of the abstract classes, each in their own
      .py file
    * __init__.py imports each of the concrete implementations, so that they are
      registered


External code can hook into the dictionary of registered methods using the
appropriate register decorator function. This decorator will execute when the
foreign code is first run, so make sure that you import your module before
requesting the dictionary of registered classes for a given step.
    
For general command line usage, it is probably easier to directly import classes
from the folder structure. The registered dictionary approach makes dynamic UI
creation easier, but it hinders autocompletion. An intermediate approach would
be to assign the results of dictionary access to a variable before instantiating
the class. For example,


.. code-block:: python

   >>> # one-shot, but autocompletion of class arguments doesn't work
   >>> model = registered_models["LDA"](tokenized_data, 5)


.. code-block:: python

   >>> model_class = registered_models["LDA"]
   >>> # Autocompletion of class arguments should work here
   >>> model = model_class(tokenized_data, 5)

 
.. code-block:: python

   >>> # import model implementation directly:
   >>> from topik.models import LDA
   >>> # Autocompletion of class arguments should work here
   >>> model = LDA(tokenized_data, 5)
