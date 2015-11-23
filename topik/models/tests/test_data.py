from topik.vectorizers.vectorizer_output import VectorizerOutput
from topik.models.base_model_output import ModelOutput

test_vectorized_output = VectorizerOutput(id_term_map={0:"frank", 1:"dog", 2:"cat", 3:"llama"},
                                          document_term_counts={"doc1": 5, "doc2": 3},
                                          doc_lengths={'doc1': 5, 'doc2': 3},
                                          term_frequency={0:1, 1:1, 2:2, 3:10},
                                          vectors={"doc1": {1: 3, 2: 1, 3: 1},
                                                   "doc2": {0: 1, 1: 1, 2: 1}})

test_model_output = ModelOutput(
    vocab={0:"frank", 1:"dog", 2:"cat", 3:"llama", 4:"airplane", 5:"stroller",
           6:"hamburger", 7:"water", 8:"shirt", 9:"cart"},
    term_frequency={0:1, 1:1, 2:2, 3:10, 4:3, 5:2, 6:9, 7:3, 8:1, 9:0},
    topic_term_matrix={'topic0': [0.060, 0.093, 0.130, 0.203, 0.122,
                                  0.034, 0.060, 0.019, 0.093, 0.186,],
                       'topic1': [0.013, 0.095, 0.169, 0.109, 0.099,
                                  0.114, 0.125, 0.087, 0.138, 0.051]},
    doc_lengths={'doc1': 3, 'doc2': 3, 'doc3': 4, 'doc4': 4},
    doc_topic_matrix={'doc1': [0.2, 0.8],
                      'doc2': [0.85, 0.15],
                      'doc3': [0.9, 0.1],
                      'doc4': [0.05, 0.95]})