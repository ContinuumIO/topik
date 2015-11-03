

def test_read_large_json(self):
    loaded_corpus = read_input('{}/test_data_large_json.json'.format(test_data_path),
                               content_field="text", json_prefix='item._source.isAuthorOf')
    ids, texts = zip(*list(iter(loaded_corpus)))
    self.assertTrue(self.solution_3_hash in ids)