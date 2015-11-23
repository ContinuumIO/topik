from topik.vectorizers.vectorizer_output import VectorizerOutput

sample_data = [("doc1", ["frank", "frank", "frank", "dog", "cat"]),
                ("doc2", ["frank", "dog", "llama"]),
               ]

output = VectorizerOutput(sample_data, lambda x, y: x)


def test_global_term_count():
    assert(output.global_term_count == 4)


def test_document_term_count():
    assert(output.document_term_counts == {"doc1": 3, "doc2": 3})

def test_term_frequency():
    # TODO: is there a better place to put this such that it gets tested on all vectorization methods?
    assert(type(output.term_frequency[1]) == int)
