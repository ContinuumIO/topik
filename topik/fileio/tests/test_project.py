import glob
import os
import time
import unittest

import elasticsearch
import nose.tools as nt
from elasticsearch.exceptions import ConnectionError
from nose.plugins.skip import SkipTest

from topik.fileio import TopikProject
from topik.fileio.tests import test_data_path

# make logging quiet during testing, to keep Travis CI logs short.
import logging
logging.basicConfig()
logging.getLogger('elasticsearch').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

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
        for filename in glob.glob("context_output*"):
            os.remove(filename)
        with TopikProject("context_output", self.output_type, self.output_args) as project:
            project.read_input(source=test_data_path, content_field='abstract')
            project.tokenize()
            project.vectorize(method='bag_of_words')
            project.run_model(model_name='lda', ntopics=2)

        # above runs through a whole workflow (minus plotting.)  At end, it closes file.
        # load output here.
        with TopikProject("context_output") as project:
            nt.assert_equal(len(list(project.get_filtered_corpus_iterator())), 100)
            nt.assert_true(sample_tokenized_doc in list(iter(project.selected_tokenized_corpus)))
            nt.assert_equal(project.selected_vectorized_corpus.global_term_count, 2434)
            nt.assert_equal(len(project.selected_vectorized_corpus), 100)  # All documents processed
            for doc in project.selected_modeled_corpus.doc_topic_matrix.values():
                nt.assert_almost_equal(sum(doc), 1)
            for topic in project.selected_modeled_corpus.topic_term_matrix.values():
                nt.assert_almost_equal(sum(topic), 1)

        for filename in glob.glob("context_output*"):
            os.remove(filename)

    def test_read_input(self):
        nt.assert_equal(len(list(self.project.get_filtered_corpus_iterator())), 100)

    def test_get_filtered_corpus_iterator(self):
        doc_list = list(self.project.get_filtered_corpus_iterator())
        nt.assert_equal(type(doc_list[0]), type(('123', 'text')))
        nt.assert_equal(len(doc_list), 100)

    def test_get_date_filtered_corpus_iterator(self):
        results = list(self.project.get_date_filtered_corpus_iterator(
            field_to_get="abstract", start=1975, end=1999, filter_field='year'))
        nt.assert_equal(len(results), 25)

    def test_tokenize(self):
        self.project.tokenize('simple')
        in_results = False
        for id, doc in self.project.selected_tokenized_corpus:
            if doc in sample_tokenized_doc:
                in_results = True
                break
        nt.assert_true(in_results)

    def test_vectorize(self):
        self.project.tokenize()
        self.project.vectorize()
        nt.assert_equal(self.project.selected_vectorized_corpus.global_term_count, 2434)
        nt.assert_equal(len(self.project.selected_vectorized_corpus), 100)  # All documents processed

    def test_model(self):
        self.project.tokenize()
        self.project.vectorize()
        self.project.run_model(model_name='lda', ntopics=2)
        for doc in self.project.selected_modeled_corpus.doc_topic_matrix.values():
            nt.assert_almost_equal(sum(doc), 1)
        for topic in self.project.selected_modeled_corpus.topic_term_matrix.values():
            nt.assert_almost_equal(sum(topic), 1)

    def test_visualize(self):
        self.project.tokenize()
        self.project.vectorize(method='bag_of_words')
        self.project.run_model(ntopics=2)
        self.project.visualize(vis_name='termite', topn=5)


class TestInMemoryOutput(unittest.TestCase, ProjectTest):
    def setUp(self):
        self.output_type = "InMemoryOutput"
        self.output_args = {}
        self.project = TopikProject("test_project",
                                    output_type=self.output_type,
                                    output_args=self.output_args)
        self.project.read_input(test_data_path, content_field="abstract")


class TestElasticSearchOutput(unittest.TestCase, ProjectTest):
    INDEX = "test_index"

    def setUp(self):
        self.output_type = "ElasticSearchOutput"
        self.output_args = {'source': 'localhost',
                            'index': TestElasticSearchOutput.INDEX,
                            'content_field': "abstract"}
        self.project = TopikProject("test_project", output_type=self.output_type,
                                    output_args=self.output_args)
        try:
            self.project.read_input(test_data_path, content_field="abstract", synchronous_wait=30)
        except ConnectionError:
            raise SkipTest("Skipping Elasticsearch test - elasticsearch not running")

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        instance.indices.delete(TestElasticSearchOutput.INDEX)
        if instance.indices.exists("{}_year_alias_date".format(TestElasticSearchOutput.INDEX)):
            instance.indices.delete("{}_year_alias_date".format(TestElasticSearchOutput.INDEX))
        time.sleep(1)
