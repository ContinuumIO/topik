import nose.tools as nt

from topik.fileio.in_elastic import elastic, ElasticSearchOutput
from topik.fileio.project import TopikProject
from topik.tests import test_data_path
from ._solutions import solution_elastic

INDEX = "test_elastic"

def test_elastic_import():
    output_args = {'source': 'localhost',
                   'index': INDEX,
                   'content_field': 'abstract'}
    # import data from file into known elastic server
    project = TopikProject(output_type='ElasticSearchOutput',
                           output_args=output_args)

    project.read_input('{}/test_data_json_stream.json'.format(
               test_data_path), content_field="abstract")#,
               #output_type=elastic.ElasticSearchOutput.class_key(),
               #output_args=output_args, synchronous_wait=30)
    loaded_corpus = elastic("localhost", source_type="elastic", index=INDEX)
    nt.assert_true(solution_elastic == next(iter(loaded_corpus))['abstract'])
