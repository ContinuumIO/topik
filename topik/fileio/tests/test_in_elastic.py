import nose.tools as nt

from topik.fileio.in_elastic import read_elastic
from topik.fileio.project import TopikProject
from topik.fileio.tests import test_data_path
from ._solutions import solution_elastic

INDEX = "test_elastic"

def test_elastic_import():
    output_args = {'source': 'localhost',
                   'index': INDEX,
                   'content_field': 'abstract'}
    # import data from file into known elastic server
    project = TopikProject("test_project", output_type='ElasticSearchOutput',
                           output_args=output_args)

    project.read_input('{}/test_data_json_stream.json'.format(
               test_data_path), content_field="abstract")#,
               #output_type=elastic.ElasticSearchOutput.class_key(),
               #output_args=output_args, synchronous_wait=30)

    loaded_corpus = read_elastic("localhost", index=INDEX)
    solution_found = False
    for doc in list(iter(loaded_corpus)):
        if solution_elastic == doc['abstract']:
            solution_found = True
            break
    nt.assert_true(solution_found)

    # tear-down
    from elasticsearch import Elasticsearch
    instance = Elasticsearch("localhost")
    if instance.indices.exists(INDEX):
        instance.indices.delete(INDEX)

