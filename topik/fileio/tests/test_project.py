import glob
import os
import unittest

from topik.fileio import TopikProject
from topik.fileio.tests import test_data_path

SAVE_FILENAME = "test_project"

sample_tokenized_doc = (2318580746137828354,
 [u'nano', u'sized', u'tio', u'particles', u'applications', u'including',
  u'use', u'photocatalysts', u'heat', u'transfer', u'fluids', u'nanofluids',
  u'present', u'study', u'tio', u'nanoparticles', u'controllable', u'phase',
  u'particle', u'size', u'obtained', u'homogeneous', u'gas', u'phase',
  u'nucleation', u'chemical', u'vapor', u'condensation', u'cvc', u'phase',
  u'particle', u'size', u'tio', u'nanoparticles', u'processing', u'conditions',
  u'characterized', u'x', u'ray', u'diffraction', u'transmission', u'electron',
  u'microscopy', u'chamber', u'temperature', u'pressure', u'key', u'parameters',
  u'affecting', u'particle', u'phase', u'size', u'pure', u'anatase', u'phase',
  u'observed', u'synthesis', u'temperatures', u'low', u'c', u'chamber',
  u'pressure', u'varying', u'torr', u'furnace', u'temperature', u'increased',
  u'c', u'pressure', u'torr', u'mixture', u'anatase', u'rutile', u'phases',
  u'observed', u'predominant', u'phase', u'anatase', u'average', u'particle',
  u'size', u'experimental', u'conditions', u'observed', u'nm'])

test_data_path = os.path.join(test_data_path, "test_data_json_stream.json")

class ProjectTest(object):
    def test_context_manager(self):
        [os.remove(f) for f in glob.glob("context_output*")]
        with TopikProject("context_output", self.output_type, self.output_args) as project:
            project.read_input(source=test_data_path, content_field='abstract')
            project.tokenize()
            project.vectorize()
            project.run_model()

        # above runs through a whole workflow (minus plotting.)  At end, it closes file.
        # load output here.
        with TopikProject("context_output") as project:
            assert(len(list(project.get_filtered_corpus_iterator())) == 100)
            # tests both contents being stored and selection of content after save/load cycle
            assert(sample_tokenized_doc in project.tokenized_corpora)
            assert(project.vectorized_corpora.global_term_count == 2434)
            assert(len(project.vectorized_corpora) == 100)  # All documents processed

        [os.remove(f) for f in glob.glob("context_output*")]

    def test_read_input(self):
        assert(len(list(self.project.get_filtered_corpus_iterator())) == 100)

    def test_get_filtered_corpus_iterator(self):
        doc_list = list(self.project.get_filtered_corpus_iterator())
        assert(type(doc_list[0]) == type(('123', 'text')))
        assert(len(doc_list) == 100)
    '''
    def test_filter_by_year(self):
        raise NotImplementedError
    '''
    def test_tokenize(self):
        self.project.tokenize('simple')
        assert(sample_tokenized_doc in self.project.output.tokenized_corpora.values()[0])

    def test_vectorize(self):
        self.project.tokenize()
        self.project.vectorize()
        assert(self.project.vectorized_corpora.global_term_count == 2434)
        assert(len(self.project.vectorized_corpora) == 100)  # All documents processed

    def test_model(self):
        self.project.tokenize()
        self.project.vectorize()
        self.project.run_model(ntopics=3)
        # TODO: these are not real tests.  Do we have numerical properties that are more meaningful?
        #   - Do weights for a given doc in doc-topic matrix sum to 1?
        #   - Do weights for all terms in a given topic sum to 1?
        assert(self.project.modeled_corpora.doc_topic_dists)
        assert(self.project.modeled_corpora.term_topic_matrix)


'''
def test_transform(self):
    raise NotImplementedError

def test_vectorize(self):
    raise NotImplementedError

def test_run_model(self):
    raise NotImplementedError

def visualize(self):
    raise NotImplementedError

def test_select_tokenized_corpora(self):
    raise NotImplementedError

def test_select_vectorized_corpora(self):
    raise NotImplementedError

def test_select_model_data(self):
    raise NotImplementedError

def test_filtered_corpus(self):
    raise NotImplementedError

def test_tokenized_corpora(self):
    raise NotImplementedError

def test_vectorized_corpora(self):
    raise NotImplementedError

def test_modeled_corpus(self):
    raise NotImplementedError

'''


class TestInMemoryOutput(unittest.TestCase, ProjectTest):
    def setUp(self):
        self.output_type = "InMemoryOutput"
        self.output_args = {}
        self.project = TopikProject("test_project",
                                    output_type=self.output_type,
                                    output_args=self.output_args)
        self.project.read_input(test_data_path, content_field="abstract")


# class TestElasticSearchOutput(unittest.TestCase, ProjectTest):
#     INDEX = "TEST_INDEX"
#     def setUp(self):
#         self.output_type = "ElasticSearchOutput"
#         self.output_args={'source': 'localhost',
#                           'index': TestElasticSearchOutput.INDEX},
#         self.project = TopikProject(output_type=self.output_type, output_args=self.output_args)
#         self.project.read_input(test_data_path, content_field="abstract",
#                                 synchronous_wait=30)
#
#     def tearDown(self):

