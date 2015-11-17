import itertools
import jsonpickle
import os

from topik import tokenizers, transformers, vectorizers, models, visualizers
from ._registry import registered_outputs
from .reader import read_input


def _get_parameters_string(**kwargs):
    """Used to create identifiers for output"""
    id=""
    if kwargs:
        id = "_" + ''.join('{}={}_'.format(key, val) for key, val in sorted(kwargs.items()))[:-1]
    return id


class TopikProject(object):
    def __init__(self, project_name, output_type=None, output_args=None, **kwargs):
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
        if os.path.exists(project_name + ".topikproject") and output_type is None:
            with open(project_name + ".topikproject") as f:
                project_data = jsonpickle.decode(f.read())
            kwargs.update(project_data)
            with open(project_name + ".topikdata") as f:
                loaded_data = jsonpickle.decode(f.read())
                output_type = loaded_data["class"]
                output_args.update(loaded_data["saved_data"])
        self.project_name = project_name
        if output_type is None:
            output_type = "InMemoryOutput"
        # loading the output here is sufficient to restore all results: the output is responsible for loading them as
        #    necessary, and returning iterators or output objects appropriately.
        self.output = registered_outputs[output_type](**output_args)
        # not used, but stored here for persistence purposes
        self._output_type = output_type
        self._output_args = output_args
        # None or a string expression in Elasticsearch query format
        self.corpus_filter = kwargs["corpus_filter"] if "corpus_filter" in kwargs else ""
        # None or a string name
        self.content_field = kwargs["content_field"] if "content_field" in kwargs else ""
        # Initially None, set to string value when tokenize or transform method called
        self._selected_source_field = kwargs["_selected_content_field"] if "_selected_content_field" in kwargs else None
        # Initially None, set to string value when tokenize or transform method called
        self._selected_tokenized_corpus = kwargs["_selected_tokenized_corpus"] if "_selected_tokenized_corpus" in kwargs else None
        # Initially None, set to string value when vectorize method called
        self._selected_vectorized_corpus = kwargs["_selected_vectorized_corpus"] if "_selected_vectorized_corpus" in kwargs else None
        # Initially None, set to string value when run_model method called
        self._selected_modeled_corpus = kwargs["_selected_modeled_corpus"] if "_selected_modeled_corpus" in kwargs else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.save()
        self.output.close()  # close any open file handles or network connections

    def save(self):
        with open(self.project_name + ".topikproject", "w") as f:
            f.write(jsonpickle.encode({"_selected_tokenized_corpus": self._selected_tokenized_corpus,
                       "_selected_vectorized_corpus": self._selected_vectorized_corpus,
                       "_selected_modeled_corpus": self._selected_modeled_corpus,
                       "corpus_filter": self.corpus_filter,
                       "project_name": self.project_name,
                       "output_type": self._output_type,
                       "output_args": self._output_args,
                       "content_field": self.content_field},
                      f))
        self.output.save(self.project_name)

    def read_input(self, source, content_field, source_type="auto", **kwargs):
        self.output.import_from_iterable(read_input(source,
                                                    content_field=content_field,
                                                    source_type=source_type,
                                                    **kwargs),
                                         content_field=content_field)
        self.content_field = content_field

    def get_filtered_corpus_iterator(self, filter_expression=None):
        if filter_expression is None:
            filter_expression = self.corpus_filter
        return self.output.get_filtered_data(filter_expression)

    def tokenize(self, method="simple", **kwargs):
        # tokenize, and store the results on this object somehow
        tokenized_corpora = tokenizers.tokenize(self.filtered_corpora,
                                             method=method, **kwargs)
        tokenize_parameter_string = self.corpus_filter + "_tk_{method}{params}".format(
            method=method,
            params=_get_parameters_string(**kwargs))

        # store this
        self.output.tokenized_corpora[tokenize_parameter_string] = tokenized_corpora
        # set _tokenizer_id internal handle to point to this data
        self._selected_tokenized_corpus = tokenize_parameter_string

    def transform(self, method, **kwargs):
        transformed_data = transformers.transform(method=method, **kwargs)
        tokenize_parameter_string = "_".join([self.tokenizer_id, "xform", method,
                                              _get_parameters_string(**kwargs)])
        # store this
        self.output.tokenized_corpora[tokenize_parameter_string] = transformed_data
        # set _tokenizer_id internal handle to point to this data
        self._selected_tokenized_corpus = tokenize_parameter_string

    def vectorize(self, method="bag_of_words", **kwargs):
        tokenizer_iterators = itertools.tee(self.tokenized_corpora)
        vectorized_corpora = vectorizers.vectorize(tokenizer_iterators[0],
                                                method=method, **kwargs)
        vectorize_parameter_string = self.corpus_filter + self._selected_tokenized_corpus + "_".join([method, _get_parameters_string(**kwargs)])
        # store this internally
        self.output.vectorized_corpora[vectorize_parameter_string] = vectorized_corpora
        # set _vectorizer_id internal handle to point to this data
        self._selected_vectorized_corpus = vectorize_parameter_string

    def run_model(self, model_name="PLSA", **kwargs):
        model_output = models.run_model(self.vectorized_corpora,
                                        model_name=model_name, **kwargs)
        model_id = "_".join([model_name, _get_parameters_string(**kwargs)])
        # store this internally
        self.output.modeled_corpora[model_id] = model_output
        # set _model_id internal handle to point to this data
        self._selected_modeled_corpus = model_id

    def visualize(self, model_id=None, **kwargs):
        if not model_id:
            model = self.model_output
        else:
            model = self.output.model_data[model_id]
        return visualizers.visualize(model, **kwargs)

    def select_tokenized_corpora(self, id):
        if id in self.output.tokenized_corpora:
            self._selected_tokenized_corpus = id
        else:
            raise ValueError("tokenized data {} not found in storage.".format(id))

    def select_vectorized_corpora(self, id):
        if id in self.output.vectorized_corpora:
            self._selected_vectorized_corpus = id
        else:
            raise ValueError("vectorized data {} not found in storage.".format(id))

    def select_model_data(self, id):
        if id in self.output.modeled_corpus:
            self._selected_modeled_corpus = id
        else:
            raise ValueError("model {} not found in storage.".format(id))

    @property
    def filtered_corpora(self):
        """Corpus documents, potentially a subset.

        Output from read_input step.
        Input to tokenization step.
        """
        return self.output.get_filtered_data(self.corpus_filter)

    @property
    def tokenized_corpora(self):
        """Documents broken into component words.  May also be transformed.

        Output from tokenization and/or transformation steps.
        Input to vectorization step.
        """
        return self.output.tokenized_corpora[self._selected_tokenized_corpus]

    @property
    def vectorized_corpora(self):
        """Data that has been vectorized into term frequencies, TF/IDF, or
        other vector representation.

        Output from vectorization step.
        Input to modeling step.
        """
        return self.output.vectorized_corpora[self._selected_vectorized_corpus]

    @property
    def modeled_corpora(self):
        """matrices representing the model derived.

        Output from modeling step.
        Input to visualization step.
        """
        return self.output.modeled_corpora[self._selected_modeled_corpus]

