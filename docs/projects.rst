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
    >>> model_output = run_model(vectors, ntopics=4)
    >>> plot = visualize(model_output)


However, this does not handle any kind of persistence to disk.  Your changes will be lost when you exit your Python session.  To unify saving all the output from all the steps together, Topik provides projects.  Here's a comparable project usage to the example above:


.. code-block:: python

    >>> from topik import TopikProject
    >>> with TopikProject("my_project") as project:
    >>>     project.read_input("./reviews/", content_field="text")
    >>>     project.tokenize()
    >>>     project.vectorize()
    >>>     project.run_model(ntopics=4)
    >>>     project.visualize()
    >>> # when project goes out of scope, any files are flushed to disk, and the project can later be loaded.


Projects create files on disk when instantiated if none already exist.  When project files already exist, the contents of those files are loaded:


.. code-block:: python

    >>> from topik import TopikProject
    >>> with TopikProject("my_project") as project:
    >>>     project.visualize()


Output formats
==============


Output formats are how your data are represented to further processing and
modeling.  Projects use a particular output format to store your intermediate results.
To ensure a uniform interface, output formats implement the interface
described by :class:`~.OutputInterface`. Presently,
two such backends are implemented:
:class:`~.InMemoryOutput` and
:class:`~.ElasticSearchOutput`. Available outputs
can be examined by checking the keys of the
:data:`topik.fileio.registered_outputs` dictionary:

.. code-block:: python

    >>> from topik.fileio import registered_outputs
    >>> list(registered_outputs.keys())


The default output is the :class:`~.InMemoryOutput`. No additional arguments
are necessary. :class:`~.InMemoryOutput` stores everything in a Python
dictionary. As such, it is memory intensive. All operations done with a
:class:`~.InMemoryOutput` block until complete. :class:`~.InMemoryOutput` is
the simplest to use, but it will ultimately limit the size of analyses that you
can perform.

The :class:`~.ElasticSearchOutput` can be specified
to :class:`~.TopikProject` using the ``output_type`` argument. It must
be accompanied by another keyword argument, ``output_args``, which should be a
dictionary containing connection details and any additional arguments.

.. code-block:: python

    >>> output_args = {"source": "localhost", "index": "destination_index", content_field="text"}
    >>> project = TopikProject("my_project", output_type="ElasticSearchOutput",
                               output_args=output_args)


:class:`~.ElasticSearchOutput` stores everything in an `Elasticsearch` instance
that you specify. Operations do not block, and have "eventual consistency": the
corpus will eventually have all of the documents you sent available, but not
necessarily immediately after the read_input function returns. This lag time is
due to `Elasticsearch` indexing the data on the server side.


Saving and loading projects
===========================

Projects are designed to help you go back to some earlier state.  There are
several dictionary-like objects accessible on the project object:

.. code-block:: python

    >>> project = TopikProject("my_project")
    >>> project.output.tokenized_corpora
    >>> project.output.vectorized_corpora
    >>> project.output.modeled_corpora


These are more quickly accessible as selected properties of the project:

.. code-block:: python

    >>> project.selected_filtered_corpus
    >>> project.selected_tokenized_corpus
    >>> project.selected_vectorized_corpus
    >>> project.selected_modeled_corpus

These selected properties keep track of the last-used technique, and give you the corresponding
data.

You can change the selected state using the :meth:`~.TopikProject.select_tokenized_corpus`,
:meth:`~.TopikProject.select_modeled_corpus`, and :meth:`~.TopikProject.select_modeled_corpus`
methods.

Project objects also persist their state to disk.  This is done in two or more files,
dependent on the output backend in use.  There will always be two files:

  * a .topikproject file, describing the project metadata and how to load the project
  * a .topikdata file, containing or describing how to obtain the data contained in the project.

Each of the above files are JSON format.  Additional files may store data in binary format.  If you
move your outputs on disk, make sure to move all of them, or Topik will not be able to load your results.

If using the project with a context manager, data is saved and connections are closed when
the context ends.  Otherwise, call the :meth:`~.OutputInterface.save` to write data
to disk, or the :meth:`~.OutputInterface.close` method to write data to disk and close
connections.

Loading projects is achieved by providing simply the project name that you provided when creating
the project.  Additional connection details will be loaded from disk automatically.

.. code-block:: python

    >>> project = TopikProject("my_project")
