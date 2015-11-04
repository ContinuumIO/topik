def test_read_documents_folder(self):
    loaded_corpus = read_input(
        '{}/test_data_folder_files'.format(test_data_path),
        content_field="abstract")
    ids, texts = zip(*list(iter(loaded_corpus)))
    self.assertTrue(self.solution_1_hash in ids)

def test_read_documents_folder_gz(self):
    loaded_corpus = read_input(
        '{}/test_data_folder_files_gz'.format(test_data_path),
        content_field="abstract")
    ids, texts = zip(*list(iter(loaded_corpus)))
    self.assertTrue(self.solution_1_hash in ids)
