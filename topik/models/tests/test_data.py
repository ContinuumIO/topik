from topik.vectorizers.vectorizer_output import VectorizerOutput
from topik.models.base_model_output import ModelOutput

test_vectorized_output = VectorizerOutput(id_term_map={0:"frank", 1:"dog", 2:"cat", 3:"llama"},
                                          document_term_counts={"doc1": 5, "doc2": 3},
                                          vectors={"doc1": {1: 3, 2: 1, 3: 1},
                                                   "doc2": {0: 1, 1: 1, 2: 1}})

#test_plsa_output = ModelOutput([[], []],
#                                        [[], []])

test_plsa_output = ModelOutput(
    vocab={0:"frank", 1:"dog", 2:"cat", 3:"llama"},
    term_frequency={0:1, 1:1, 2:2, 3:10},
    topic_term_matrix={'topic0': {0:0.1, 1:0.9, 2:0.05, 3:0.8},
                       'topic1': {0:0.9, 2:0.1, 2:0.95, 3:0.2}},
    doc_lengths={'doc1': 3, 'doc2': 3, 'doc3': 4, 'doc4': 4},
    doc_topic_matrix={'doc1': {'topic0': 0.2, 'topic1': 0.8},
                      'doc2': {'topic0': 0.85, 'topic1': 0.15},
                      'doc3': {'topic0': 0.9, 'topic1': 0.1},
                      'doc4': {'topic0': 0.05, 'topic1': 0.95}})