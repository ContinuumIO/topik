import os
import unittest

from topik.fileio import TopikProject
from topik.fileio.tests import test_data_path
from topik.fileio import registered_outputs

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

class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.test_project = TopikProject()

    def test_read_input(self):
        self.test_project.read_input(source=test_data_path, content_field='abstract')
        print(list(self.test_project.get_filtered_corpus_iterator()))
        assert(len(list(self.test_project.get_filtered_corpus_iterator())) == 100)

    def test_get_filtered_corpus_iterator(self):
        self.test_project.read_input(source=test_data_path, content_field='abstract')
        doc_list = list(self.test_project.get_filtered_corpus_iterator())
        print(doc_list)
        assert(type(doc_list[0]) == type(('123','text')))
        assert(len(doc_list) == 100)

    def test_tokenize(self):
        self.test_project.read_input(source=test_data_path, content_field='abstract')
        self.test_project.tokenize('simple')
        print('+'*20)
        tokenized_corpus = list(self.test_project.output.get_filtered_data(
            self.test_project._selected_tokenizer))
        print(tokenized_corpus)
        assert(sample_tokenized_doc in tokenized_corpus)
        print('+'*20)
'''
    def test_transform(self):
        raise NotImplementedError

    def test_vectorize(self):
        raise NotImplementedError

    def test_run_model(self):
        raise NotImplementedError

    def visualize(self):
        raise NotImplementedError

    def test_select_tokenized_data(self):
        raise NotImplementedError

    def test_select_vectorized_data(self):
        raise NotImplementedError

    def test_select_model_data(self):
        raise NotImplementedError

    def test_filtered_corpus(self):
        raise NotImplementedError

    def test_tokenized_data(self):
        raise NotImplementedError

    def test_vectorized_data(self):
        raise NotImplementedError

    def test_modeled_corpus(self):
        raise NotImplementedError

'''


    '''
    def test_read_input_elastic(self):
        elastic_output_args = {'source':'localhost','index':'topik_unittest',
                                'content_field':'abstract'}
        with TopikProject(output_type="ElasticSearchOutput",
                          output_args=elastic_output_args) as project:
            project.read_input(source=test_data_path, content_field='abstract')
            print(list(project.get_filtered_corpus_iterator()))
            assert(len(list(project.get_filtered_corpus_iterator())) == 100)
    '''

def test_in_memory_project_read():
    with TopikProject() as test_project:
        test_project.read_input(source=test_data_path, content_field='abstract')
        print(list(test_project.filtered_corpus))
        assert(len(list(test_project.get_filtered_corpus_iterator())) == 100)