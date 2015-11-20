import numpy as np
import pandas as pd


def get_top_words(vectorized_output, topic_term_matrix, topn):
    top_words = []
    # each "topic" is a row of the dz matrix
    for topic in topic_term_matrix:
        word_ids = np.argpartition(topic, -topn)[-topn:]
        word_ids = reversed(np.array(word_ids)[np.argsort(np.array(topic)[word_ids])])
        top_words.append([(topic[word_id], vectorized_output.id_term_map[word_id]) for word_id in word_ids])
    return top_words

def termite_data(vectorized_output, topic_term_matrix, topn=15):
    """generate the pandas dataframe input for the termite plot.

    parameters
    ----------
    topn_words : int
        number of words to include from each topic

    examples
    --------


    >> model = load_model(os.path.join(os.path.dirname(os.path.realpath("__file__")),
    >> model = load_model('{}/doctest.model'.format(test_data_path),
    ...                    model_name="lda_3_topics")
    >> model.termite_data(5)
        topic    weight           word
    0       0  0.005735             nm
    1       0  0.005396          phase
    2       0  0.005304           high
    3       0  0.005229     properties
    4       0  0.004703      composite
    5       1  0.007056             nm
    6       1  0.006298           size
    7       1  0.005977           high
    8       1  0.005291  nanoparticles
    9       1  0.004737    temperature
    10      2  0.006557           high
    11      2  0.005302      materials
    12      2  0.004439  nanoparticles
    13      2  0.004219           size
    14      2  0.004149              c

    """
    from itertools import chain
    return pd.DataFrame(list(chain.from_iterable([{"topic": topic_id, "weight": weight, "word": word}
                                                  for (weight, word) in topic]
                                                 for topic_id, topic in enumerate(get_top_words(vectorized_output=vectorized_output,
                                                                                  topic_term_matrix=topic_term_matrix, topn=topn)))))

def to_py_lda_vis(doc_data_df, term_data_df, model_data):
    model_lda_vis_data = {  'vocab': term_data_df['term'],
                            'term_frequency': term_data_df['term_frequency'],
                            'topic_term_dists': term_data_df.iloc[:,:-2].T,
                            'doc_topic_dists': doc_data_df.iloc[:,:-1],
                            'doc_lengths': doc_data_df['doc_length']}
    return model_lda_vis_data
