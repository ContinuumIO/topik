from topik.vectorizers.vectorizer_output import VectorizerOutput

test_vectorized_output = VectorizerOutput(global_terms=["frank", "dog", "cat", "llama"],
                                          document_term_counts={"doc1": 5, "doc2": 3},
                                          vectors={"doc1": {1: 3, 2: 1, 3: 1},
                                                   "doc2": {0: 1, 1: 1, 2: 1}})
