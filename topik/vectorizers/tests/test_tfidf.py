from topik.vectorizers.tfidf import tfidf

sample_data = [("doc1", ["frank", "frank", "frank", "dog", "cat"]),
                ("doc2", ["frank", "dog", "llama"]),
               ]

output = tfidf(sample_data)

def test_vectorize():
   assert output.vectors == {"doc1": {1: 0.0, 2: 0.0, 3: 0.69314718056},
                             "doc2": {0: 0.69314718056, 1: 0.0, 2: 0.0}}
