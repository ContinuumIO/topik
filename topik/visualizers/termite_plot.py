import blaze as blz

from odo import into
import numpy as np
import pandas as pd
from bokeh import plotting as plt
from bokeh.models import sources

from ._registry import register
from topik.models.tests.test_data import test_model_output


def _get_top_words(modeled_corpus, topn):
    top_words = []
    # each "topic" is a row of the dz matrix
    for topic_id, topic_term_dist in modeled_corpus.topic_term_matrix.items():
        word_ids = np.argpartition(topic_term_dist, -topn)[-topn:]
        word_ids = reversed(np.array(word_ids)[np.argsort(np.array(topic_term_dist)[word_ids])])
        top_words.append([(int(topic_id[5:]), topic_term_dist[word_id],
                           modeled_corpus.vocab[word_id]) for word_id in word_ids])
    return top_words


def _termite_data(modeled_corpus, topn):
    top_words = _get_top_words(modeled_corpus, topn=topn)
    from itertools import chain
    top_words_df = pd.DataFrame(list(chain.from_iterable([{"topic": topic_id, "weight": weight, "word": word}
                                                  for topic_id, weight, word in topic] for topic in top_words)))
    return top_words_df.sort('topic')


@register
def termite(modeled_corpus, plot_title="Termite plot", topn=15):
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
    >>> plot = termite(test_model_output, plot_title="My model results", topn=5)

    """
    prepared_model_vis_data = _termite_data(modeled_corpus, topn)

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

    data_source = sources.ColumnDataSource(source)

    p = plt.figure(x_range=TOPICS, y_range=WORDS,
                   plot_width=1000, plot_height=1700,
                   title=plot_title)

    p.circle(x="topic", y="word", size="size", fill_alpha=0.6, source=data_source)
    return p


def termite_html(modeled_corpus, filename, plot_title="Termite plot", topn=15):
    plt.output_file(filename, plot_title)
    p = termite(modeled_corpus, plot_title=plot_title, topn=topn)
    plt.save(obj=p)