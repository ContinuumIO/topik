Topik Projects
##############

Topik can be run by chaining the output of one step directly to the input of another:

.. code-block:: python

    >>> from topik import read_input, tokenize, vectorize, run_model, visualize
    >>> raw_data = read_input("./reviews/")
    >>> content_field = "text"
    >>> raw_data = ((hash(item[content_field]), item[content_field]) for item in raw_data)
    >>> tokens = tokenize(raw_data)
    >>> vectors = vectorize(tokens)
    >>> model_output = model(vectors, ntopics=4)
    >>> plot = visualize(model_output)


However, this does not handle any kind of persistence to disk.  Your changes will be lost when you exit your Python session.  To unify saving all the output from all the steps together, Topik provides projects.  Here's a comparable project usage to the example above:


.. code-block:: python

    >>> with TopikProject("my_project") as project:
    >>>     project.read_input("./reviews/", content_field="text")
    >>>     project.tokenize()
    >>>     project.vectorize()
    >>>     project.model(ntopics=4)
    >>>     project.plot()
    >>> # when project goes out of scope, any files are flushed to disk, and the project can later be loaded.


Projects create files on disk when instantiated if none already exist.  When project files already exist, the contents of those files are loaded:


.. code-block:: python

    >>> with TopikProject("my_project") as project:
    >>>     project.plot()



