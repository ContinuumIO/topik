import glob
import os
import time
import unittest

import elasticsearch

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
            print('sample_tokenized_doc')
            print(sample_tokenized_doc)
            print('project.selected_tokenized_corpus')
            print(type(list(project.selected_tokenized_corpus)))
            print(list(project.selected_tokenized_corpus))
            print(type(list(iter(project.selected_tokenized_corpus))))
            print(list(iter(project.selected_tokenized_corpus)))
            print(list(iter(project.selected_tokenized_corpus))[0])
            print(sample_tokenized_doc in list(iter(project.selected_tokenized_corpus)))
            #assert(sample_tokenized_doc in list(iter(project.selected_tokenized_corpus)))
            assert(project.selected_vectorized_corpus.global_term_count == 2434)
            assert(len(project.selected_vectorized_corpus) == 100)  # All documents processed

        [os.remove(f) for f in glob.glob("context_output*")]

    def test_read_input(self):
        assert(len(list(self.project.get_filtered_corpus_iterator())) == 100)

    def test_get_filtered_corpus_iterator(self):
        doc_list = list(self.project.get_filtered_corpus_iterator())
        assert(type(doc_list[0]) == type(('123', 'text')))
        assert(len(doc_list) == 100)

    def test_get_date_filtered_corpus_iterator(self):
        results = list(self.project.get_date_filtered_corpus_iterator(
            field_to_get="abstract", start=1975, end=1999, filter_field='year'))
        assert(len(results) == 25)

    def test_tokenize(self):
        self.project.tokenize('simple')
        in_results = False
        for id, doc in self.project.selected_tokenized_corpus:
            if doc in sample_tokenized_doc:
                in_results = True
                break
        assert(in_results)

    def test_vectorize(self):
        self.project.tokenize()
        self.project.vectorize()
        assert(self.project.selected_vectorized_corpus.global_term_count == 2434)
        assert(len(self.project.selected_vectorized_corpus) == 100)  # All documents processed

    def test_model(self):
        self.project.tokenize()
        self.project.vectorize()
        self.project.run_model()
        # TODO: these are not real tests.  Do we have numerical properties that are more meaningful?
        #   - Do weights for a given doc in doc-topic matrix sum to 1?
        #   - Do weights for all terms in a given topic sum to 1?
        print(self.project.selected_modeled_corpus.doc_topic_matrix)
        print("Testing DTM SUMS")
        # assert([sum(self.project.selected_modeled_corpus.doc_topic_matrix[doc_id]) == 1 \
        #     for doc_id in self.project.selected_modeled_corpus.doc_topic_matrix])
        for doc_id in self.project.selected_modeled_corpus.doc_topic_matrix:
            print('SUMMING_DOC')
            print(doc_id,sum(self.project.selected_modeled_corpus.doc_topic_matrix[doc_id]))
            # assert(sum(self.project.selected_modeled_corpus.doc_topic_matrix[doc_id])==1)

        print("TESTING TTM SUMS")
        for topic_id in self.project.selected_modeled_corpus.topic_term_matrix:
            print('SUMMING_TERM')
            print(topic_id,sum(self.project.selected_modeled_corpus.topic_term_matrix[topic_id]))
            # assert(sum(self.project.selected_modeled_corpus.topic_term_matrix[topic_id])==1)

    def test_visualize(self):
        self.project.tokenize()
        self.project.vectorize()
        self.project.run_model()
        self.project.visualize(topn=5)



    # def test_transform(self):
    #     raise NotImplementedError
    #
    # def test_select_tokenized_corpora(self):
    #     raise NotImplementedError
    #
    # def test_select_vectorized_corpora(self):
    #     raise NotImplementedError
    #
    # def test_select_model_data(self):
    #     raise NotImplementedError
    #
    # def test_filtered_corpus(self):
    #     raise NotImplementedError
    #
    # def test_tokenized_corpora(self):
    #     raise NotImplementedError
    #
    # def test_vectorized_corpora(self):
    #     raise NotImplementedError
    #
    # def test_modeled_corpus(self):
    #     raise NotImplementedError


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
        self.project.read_input(test_data_path, content_field="abstract",
                                synchronous_wait=30)

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        instance.indices.delete(TestElasticSearchOutput.INDEX)
        if instance.indices.exists("{}_year_alias_date".format(TestElasticSearchOutput.INDEX)):
            instance.indices.delete("{}_year_alias_date".format(TestElasticSearchOutput.INDEX))
        time.sleep(1)
