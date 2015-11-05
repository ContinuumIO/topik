from topik.vectorizers.bag_of_words import bag_of_words

sample_data = [("doc1", ["frank", "frank", "frank", "dog", "cat"]),
                ("doc2", ["frank", "dog", "llama"]),
               ]

output = bag_of_words(sample_data)



def test_vectorizer():
    assert(output.vectors["doc1"] == {1: 3, 2: 1, 3: 1})
    assert(output.vectors["doc2"] == {0: 1, 1: 1, 2: 1})
