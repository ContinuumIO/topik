from topik.tokenizers.simple import simple, _simple_document

sample_data = [("doc1", "frank FRANK the frank dog cat"),
                ("doc2", "frank a dog of the llama"),
               ]

def test__simple_document():
    assert(_simple_document(sample_data[0][1]) == ["frank", "frank", "frank",
                                                   "dog", "cat"])

def test_simple():
    tokenized_corpora = simple(sample_data)
    assert(next(tokenized_corpora) == ("doc1", ["frank", "frank", "frank", "dog", "cat"]))
    assert(next(tokenized_corpora) == ("doc2", ["frank", "dog", "llama"]))