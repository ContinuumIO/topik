import blaze as blz

from odo import into
import pandas as pd
import bokeh.plotting as plt
from bokeh.models.sources import ColumnDataSource

from ._registry import register
from .data_formatters import termite_data
from topik.models.tests.test_data import test_vectorized_output, test_plsa_output


@register
def termite(input_data, plot_title="Termite plot", output_file="termite.html"):
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
    >>> plot_input = termite_data()
    >>> termite = termite(termite_data,
    ...                   "My lda results")

    """

    t = blz.Data(input_data)

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

