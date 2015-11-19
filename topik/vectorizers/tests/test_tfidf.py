import nose.tools as nt

from topik.vectorizers.tfidf import tfidf

sample_data = [("doc1", ["frank", "frank", "frank", "dog", "cat"]),
                ("doc2", ["frank", "dog", "llama"]),
               ]

output = tfidf(sample_data)

def test_vectorize():
    reference = {"doc1": {1: 0.0, 2: 0.0, 3: 0.69314718056},
                 "doc2": {0: 0.69314718056, 1: 0.0, 2: 0.0}}
    for doc_id, doc in output.vectors.items():
        for word, val in doc.items():
            nt.assert_almost_equal(val, reference[doc_id][word])
