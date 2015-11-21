import blaze as blz

from odo import into
import numpy as np
import pandas as pd
import bokeh.plotting as plt
from bokeh.models.sources import ColumnDataSource

from ._registry import register
from topik.models.tests.test_data import test_vectorized_output, test_plsa_output

def _get_top_words(vectorized_output, topic_term_matrix, topn):
    top_words = []
    # each "topic" is a row of the dz matrix
    for topic_id, topic_term_dist in topic_term_matrix.items():
        word_ids = np.argpartition(topic_term_dist, -topn)[-topn:]
        word_ids = reversed(np.array(word_ids)[np.argsort(np.array(topic_term_dist)[word_ids])])
        top_words.append([(int(topic_id[5:]),topic_term_dist[word_id], vectorized_output.vocab[word_id]) for word_id in word_ids])
    return top_words

def _termite_data(vectorized_output, topic_term_matrix, topn):
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
    top_words = _get_top_words(vectorized_output=vectorized_output, topic_term_matrix=topic_term_matrix, topn=topn)
    from itertools import chain
    top_words_df = pd.DataFrame(list(chain.from_iterable([{"topic": topic_id, "weight": weight, "word": word}
                                                  for topic_id, weight, word in topic] for topic in top_words)))
    return top_words_df.sort('topic')

@register
def termite(modeled_corpus, plot_title="Termite plot", output_file="termite.html", topn=15):
    """A Bokeh Termite Visualization for LDA results analysis.

    Parameters
    ----------
    input_file : str or pandas DataFrame
        A pandas dataframe from a topik model get_termite_data() containing columns "word", "topic" and "weight".
        May also be a string, in which case the string is a filename of a csv file with the above columns.
    title : str
        The title for your termite plot

    Examples
    --------
    >>> plot_input = _termite_data()
    >>> termite = termite(_termite_data,
    ...                   "My lda results")

    """
    prepared_model_vis_data = _termite_data(modeled_corpus, modeled_corpus.topic_term_matrix, topn)

    t = blz.Data(prepared_model_vis_data)

    MAX = blz.compute(t.weight.max())
    MIN = blz.compute(t.weight.min())

    # Create a size variable to define the size of the the circle for the plot.
    t = blz.transform(t, size=blz.sqrt((t.weight - MIN)/(MAX - MIN))*50)

    WORDS = t['word'].distinct()
    WORDS = into(list, WORDS)
    topics = t['topic'].distinct()
    topics = into(list, topics)
    # Convert topics to strings
    TOPICS = [str(i) for i in topics]

    source = into(pd.DataFrame, t)

    plt.output_file(output_file)

    data_source = ColumnDataSource(source)

    p = plt.figure(x_range=TOPICS, y_range=WORDS,
                   plot_width=1000, plot_height=1700,
                   title=plot_title)

    p.circle(x="topic", y="word", size="size", fill_alpha=0.6, source=data_source)
    plt.show(p)

