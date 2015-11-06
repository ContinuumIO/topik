Topik Projects
##############

Topik can be run by chaining the output of one step directly to the input of another:

.. code-block:: python
    >>> from topik.file_io import read_input
    >>> from topik.tokenizers import tokenize
    >>> from topik.vectorizers import vectorize
    >>> from topik.models import model
    >>> from topik.visualizers import visualize
    >>> raw_data = read_input("test_data.json")
    >>> tokens = tokenize(raw_data)
    >>> vectors = vectorize(tokens)
    >>> model_output = model(vectors)
    >>> plot = visualize(model_output)


However, this does not handle any kind of persistence to disk.  Your changes will be lost when you exit your Python session.  To unify saving all the output from all the steps together, Topik provides projects.  Here's a comparable project usage to the example above:


.. code-block:: python
    >>> with TopikProject() as project:
    >>>     project.read_input("test_data.json")
    >>>     project.tokenize()
    >>>     project.vectorize()
    >>>     project.model()
    >>>     project.plot()
    >>> # when project goes out of scope, any files are flushed to disk, and the project can later be loaded.


Projects create files on disk when instantiated if none already exist.  When project files already exist, the contents of those files are loaded:

.. code-block:: python
    >>> with TopikProject() as project:
    >>>     project.plot()



