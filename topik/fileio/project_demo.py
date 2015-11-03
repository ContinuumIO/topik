import functools

from topik.tokenizers import tokenize
from topik.vectorizers import vectorize
from topik.models import run_model
from topik.visualizers import visualize


class TopikProject(object):
    active_project = None
    corpus_filter = None
    corpus_filters = []  # collection of existing corpus filters
    corpus = None

    def __init__(self, *args, **kwargs):
        super(TopikProject, self).__init__(*args, **kwargs)

    def load_corpus(self):
        raise NotImplementedError

    def get_filtered_corpus_iterator(self, filter_expression=None):
        if filter_expression is None:
            filter_expression = self.corpus_filter
        return self.corpus.


    def tokenize(self, method, **kwargs):
        # tokenize, and store the results on this object somehow
        tokenized_data = tokenize(self.get_filtered_corpus_iterator(),
                                  method=method, **kwargs)
        tokenize_parameter_string="tk_{method}_{params}".format(
            method=method,
            params="_".join())
        # store this


    def vectorize(self, method="", **kwargs):
        vectorized_data = vectorize(self.get_tokenized_text_iterator(),
                                    method=method, **kwargs)
        # store this internally

        # set _vectorized_data internal handle to point to this data


    def run_model(self, model_name, **kwargs):
        model_output = run_model(self.vectorized_data,
                                  model_name=model_name, **kwargs)
        # store this internally
        # set _model_output internal handle to point to this data

    def visualize(self, *args, **kwargs):
        return functools.partial(visualize, project=self, *args, **kwargs)


    @property
    def filtered_corpus(self):
        """Corpus documents, potentially a subset.

        Output from read_input step.
        Input to tokenization step.
        """
        raise NotImplementedError

    @property
    def tokenized_data(self):
        """Documents broken into component words.  May also be transformed.

        Output from tokenization and/or transformation steps.
        Input to vectorization step.
        """
        raise NotImplementedError

    @property
    def vectorized_data(self):
        """Data that has been vectorized into term frequencies, TF/IDF, or
        other vector representation.

        Output from vectorization step.
        Input to modeling step.
        """
        raise NotImplementedError

    @property
    def model_output(self):
        """matrices representing the model derived.

        Output from modeling step.
        Input to visualization step.
        """
        raise NotImplementedError


# Example usage: utilize a context manager to keep track of this project.
#    Methods are called on that object as a very thin convenience layer
#    to pass the project object to other functionst that do stuff.
"""
with TopikProject("filename", parameters_for_backend) as project:
    raw_input = read_input(file_to_load, project, )
    # apply filters
    filtered_data = raw_input.filter()
    result = project.tokenize(filtered_data, method=, data_filters)
    vectorize(project, method=, OR specify tokenization method) # if
"""

