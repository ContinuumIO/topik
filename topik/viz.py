from __future__ import absolute_import

import logging

from topik.tests import test_data_path

class Termite(object):
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
    >>> termite = Termite("{}/termite.csv".format(test_data_path),
    ...                   "My lda results")
    >>> termite.plot('my_termite.html')

    """
    def __init__(self, input_file, title):
        self.input_file = input_file
        self.title = title

    def plot(self, output_file="termite.html"):
        import blaze as blz
        from odo import into
        import pandas as pd
        import bokeh.plotting as plt
        from bokeh.models.sources import ColumnDataSource

        t = blz.Data(self.input_file)

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
                       title=self.title)

        p.circle(x="topic", y="word", size="size", fill_alpha=0.6, source=data_source)
        plt.show(p)

def plot_lda_vis(model_data):
    """Designed to work with to_py_lda_vis() in the model classes."""
    from pyLDAvis import prepare, show
    model_vis_data = prepare(**model_data)
    show(model_vis_data)
