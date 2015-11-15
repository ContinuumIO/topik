from topik import tokenizers, transformers, vectorizers, models, visualizers
from ._registry import registered_outputs
from .reader import read_input


def _get_parameters_string(**kwargs):
    """Used to create identifiers for output"""
    id = ''.join('{}={}_'.format(key, val) for key, val in sorted(kwargs.items()))
    return id[:-1]


class TopikProject(object):
    def __init__(self, output_type="InMemoryOutput", output_args=None, **kwargs):
        """Class that abstracts persistence.  Drives different output types, and handles
        storing intermediate results to given output type.

        output_type : string
            internal format for handling user data.  Current options are
            present in topik.fileio.registered_outputs.  default is "InMemoryOutput".
        output_args : dictionary or None
            configuration to pass through to output
        synchronous_wait : integer
            number of seconds to wait for data to finish uploading to output, when using an asynchronous
             output type.  Only relevant for some output types ("ElasticSearchOutput", not "InMemoryOutput")
        **kwargs : passed through to superclass __init__.  Not passed to output.
        """
        if output_args is None:
            output_args = {}
        # loading the output here is sufficient to restore all results: the output is responsible for loading them as
        #    necessary, and returning iterators or output objects appropriately.
        self.output = registered_outputs[output_type](**output_args)
        # None or a string expression in Elasticsearch query format
        self.corpus_filter = kwargs["corpus_filter"] if "corpus_filter" in kwargs else None
        # Initially None, set to string value when tokenize or transform method called
        self._tokenizer_id = kwargs["_tokenizer_id"] if "_tokenizer_id" in kwargs else None
        # Initially None, set to string value when vectorize method called
        self._vectorizer_id = kwargs["_vectorizer_id"] if "_vectorizer_id" in kwargs else None
        # Initially None, set to string value when run_model method called
        self._model_id = kwargs["_model_id"] if "_model_id" in kwargs else None
        super(TopikProject, self).__init__(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        #self.output.persist()
        #self.output.close()  # close any open file handles or network connections

    def read_input(self, source, content_field, source_type="auto", **kwargs):
        self.output.import_from_iterable(read_input(source,
                                                    content_field=content_field,
                                                    source_type=source_type,
                                                    **kwargs),
                                         content_field=content_field)

    def get_filtered_corpus_iterator(self, filter_expression=None):
        if filter_expression is None:
            filter_expression = self.corpus_filter
        return self.output.get_filtered_data(filter_expression)

    def tokenize(self, method, **kwargs):
        # tokenize, and store the results on this object somehow
        tokenized_data = tokenizers.tokenize(self.filtered_corpus,
                                             method=method, **kwargs)
        tokenize_parameter_string="tk_{method}_{params}".format(
            method=method,
            params=_get_parameters_string(**kwargs))

        # store this
        self.output.append_from_iterable(tokenized_data,
                                         tokenize_parameter_string)
        #self.output.token_data[tokenize_parameter_string] = tokenized_data
        # set _tokenizer_id internal handle to point to this data
        self._tokenizer_id = tokenize_parameter_string

    def transform(self, method, **kwargs):
        transformed_data = transformers.transform(method=method, **kwargs)
        tokenize_parameter_string = "_".join([self.tokenizer_id, "xform", method,
                                              _get_parameters_string(**kwargs)])
        # store this
        self.output.tokenized_data[tokenize_parameter_string] = transformed_data
        # set _tokenizer_id internal handle to point to this data
        self._tokenizer_id = tokenize_parameter_string

    def vectorize(self, method="", **kwargs):
        vectorized_data = vectorizers.vectorize(self.tokenized_data,
                                                method=method, **kwargs)
        vectorize_parameter_string = "_".join([method, _get_parameters_string(**kwargs)])
        # store this internally
        self.output.vectorized_data[vectorize_parameter_string] = vectorized_data
        # set _vectorizer_id internal handle to point to this data
        self._vectorizer_id = vectorize_parameter_string

    def run_model(self, model_name, **kwargs):
        model_output = models.run_model(self.vectorized_data,
                                        model_name=model_name, **kwargs)
        model_id = "_".join([model_name, _get_parameters_string(**kwargs)])
        # store this internally
        self.output.model_data[model_id] = model_output
        # set _model_id internal handle to point to this data
        self._model_id = model_id

    def visualize(self, model_id=None, **kwargs):
        if not model_id:
            model = self.model_output
        else:
            model = self.output.model_data[model_id]
        return visualizers.visualize(model, **kwargs)

    def select_tokenized_data(self, id):
        if id in self.tokenizer_ids:
            self.selected_tokenizer = id
        else:
            raise ValueError("tokenized data {} not found in storage.".format(id))

    def select_vectorized_data(self, id):
        if id in self.output.vectorized_data:
            self.selected_vectorizer = id
        else:
            raise ValueError("vectorized data {} not found in storage.".format(id))

    def select_model_data(self, id):
        if id in self.output.model_data:
            self.selected_model = id
        else:
            raise ValueError("model {} not found in storage.".format(id))

    @property
    def filtered_corpus(self):
        """Corpus documents, potentially a subset.

        Output from read_input step.
        Input to tokenization step.
        """
        return self.output.get_filtered_data(self.corpus_filter)

    @property
    def tokenized_data(self):
        """Documents broken into component words.  May also be transformed.

        Output from tokenization and/or transformation steps.
        Input to vectorization step.
        """
        return self.output.tokenized_data[self._tokenizer_id]

    @property
    def vectorized_data(self):
        """Data that has been vectorized into term frequencies, TF/IDF, or
        other vector representation.

        Output from vectorization step.
        Input to modeling step.
        """
        return self.output.vectorized_data[self._vectorizer_id]

    @property
    def model_output(self):
        """matrices representing the model derived.

        Output from modeling step.
        Input to visualization step.
        """
        return self.output.model_data[self._model_id]

