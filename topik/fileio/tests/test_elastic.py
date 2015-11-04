def test_elastic_import(self):
    output_args = {'source': 'localhost',
                   'index': INDEX}
    # import data from file into known elastic server
    read_input('{}/test_data_json_stream.json'.format(
               test_data_path), content_field="abstract",
               output_type=ElasticSearchCorpus.class_key(),
               output_args=output_args, synchronous_wait=30)
    loaded_corpus = read_input("localhost", source_type="elastic", content_field="abstract", index=INDEX)
    ids, texts = zip(*list(iter(loaded_corpus)))
    self.assertTrue(self.solution_4_hash in ids
