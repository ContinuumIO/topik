from topik.vectorizers.vectorizer_output import VectorizerOutput
from topik.models.base_model_output import TopicModelResultBase

test_vectorized_output = VectorizerOutput(id_term_map={0:"frank", 1:"dog", 2:"cat", 3:"llama"},
                                          document_term_counts={"doc1": 5, "doc2": 3},
                                          vectors={"doc1": {1: 3, 2: 1, 3: 1},
                                                   "doc2": {0: 1, 1: 1, 2: 1}})

test_plsa_output = TopicModelResultBase([[], []],
                                        [[], []])