import functools

from topik.tokenizers import tokenize
from topik.vectorizers import vectorize
from topik.models import train_model
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


    def tokenize(self, **kwargs):
        # tokenize, and store the results on this object somehow
         = tokenize(self.get_filtered_corpus_iterator(), **kwargs)
        # store this
        return functools.partial(tokenize, project=self, *args, **kwargs)

    def vectorize(self, *args, **kwargs):
        return functools.partial(vectorize, project=self, *args, **kwargs)

    def train_model(self, *args, **kwargs):
        return functools.partial(train_model, project=self, *args, **kwargs)

    def visualize(self, *args, **kwargs):
        return functools.partial(visualize, project=self, *args, **kwargs)



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

