"""
This file demonstrates a bokeh applet, which can either be viewed
directly on a bokeh-server, or embedded into a flask application.
See the README.md file in this directory for instructions on running.
"""

import logging

logging.basicConfig(level=logging.DEBUG)

import numpy as np
import pandas as pd

from bokeh.models import ColumnDataSource, Plot
from bokeh.plotting import figure, curdoc
from bokeh.properties import String, Instance
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select

import topik

# cache stock data as dict of pandas DataFrames
pd_cache = {}

def get_data(analysis_name, model, **params):
    return topik.read_project(analysis_name, model, **params)


class TopikApp(VBox):
    extra_generated_classes = [["TopikApp", "VBox"]]
    jsmodel = "VBox"

    # text statistics
    pretext = Instance(PreText)

    # plots
    termite_plot = Instance(Plot)

    # data source
    source = Instance(ColumnDataSource)

    # layout boxes
    mainrow = Instance(HBox)
    histrow = Instance(HBox)
    statsbox = Instance(VBox)

    # inputs
    data_source_type = String(default=next(topik.readers.registered_inputs.keys()))
    model_type = String(default=next(topik.models.registered_models.keys()))

    data_source_select = Instance(Select)
    model_select = Instance(Select)
    input_box = Instance(VBoxForm)

    def __init__(self, *args, **kwargs):
        super(TopikApp, self).__init__(*args, **kwargs)
        self._dfs = {}

    @classmethod
    def create(cls):
        """
        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        # create layout widgets
        obj = cls()
        obj.mainrow = HBox()
        obj.histrow = HBox()
        obj.statsbox = VBox()
        obj.input_box = VBoxForm()

        # create input widgets
        obj.make_inputs()

        # outputs
        obj.pretext = PreText(text="", width=500)
        obj.make_source()
        obj.make_plots()
        obj.make_stats()

        # layout
        obj.set_children()
        return obj

    def make_inputs(self):
        available_models = list(topik.models.registered_models.keys())
        available_inputs = list(topik.readers.registered_inputs.keys())

        self.data_source_select = Select(
            name="Input source",
            value=available_inputs[0],
            options=available_inputs
        )
        self.model_select = Select(
            name='Models',
            value=available_models[0],
            options=available_models
        )

    def get_input_parameter_ui(self, input_type):
        """Create appropriate UI elements to represent input parameters to given input type.

        :return:
        """
        raise NotImplementedError

    @property
    def selected_df(self):
        pandas_df = self.df
        selected = self.source.selected['1d']['indices']
        if selected:
            pandas_df = pandas_df.iloc[selected, :]
        return pandas_df

    def make_source(self):
        self.source = ColumnDataSource(data=self.df)

    def make_termite_plot(self):
        t = blz.Data(self.input_file)

        max_weight = blz.compute(t.weight.max())
        min_weight = blz.compute(t.weight.min())

        # Create a size variable to define the size of the the circle for the plot.
        t = blz.transform(t, size=blz.sqrt((t.weight - min_weight)/(max_weight - min_weight))*50)

        WORDS = t['word'].distinct()
        WORDS = into(list, WORDS)
        topics = t['topic'].distinct()
        topics = into(list, topics)
        # Convert topics to strings
        TOPICS = [str(i) for i in topics]

        source = into(pd.DataFrame, t)

        data_source = ColumnDataSource(source)

        p = figure(x_range=self.number_topics, y_range=self.get_number_words(),
                   plot_width=1000, plot_height=1700,
                   title="Termite plot of {} with ".format(self.model_type, self.model_params))

        p.circle(x="topic", y="word", size="size", fill_alpha=0.6, source=data_source)
        #p.xaxis().major_label_orientation = np.pi/3
        logging.info("generating termite plot for file %s" % self.input_file)
        plt.show(p)

    def make_plots(self):
        self.termite_plot = self.make_termite_plot()

    def set_children(self):
        self.children = [self.mainrow, self.histrow, self.line_plot1, self.line_plot2]
        self.mainrow.children = [self.input_box, self.plot, self.statsbox]
        self.input_box.children = [self.ticker1_select, self.ticker2_select]
        self.histrow.children = [self.hist1, self.hist2]
        self.statsbox.children = [self.pretext]

    def input_change(self, obj, attrname, old, new):
        if obj == self.model_select:
            self.model_type = new
        if obj == self.data_source_select:
            self.data_source_type = new

        self.make_source()
        self.make_plots()
        self.set_children()
        curdoc().add(self)

    def setup_events(self):
        super(TopikApp, self).setup_events()
        if self.source:
            self.source.on_change('selected', self, 'selection_change')
        if self.model_select:
            self.model_select.on_change('value', self, 'input_change')
        if self.data_source_select:
            self.data_source_select.on_change('value', self, 'input_change')

    def make_stats(self):
        stats = self.selected_df.describe()
        self.pretext.text = str(stats)

    def selection_change(self, obj, attrname, old, new):
        self.make_stats()
        self.hist_plots()
        self.set_children()
        curdoc().add(self)

    @property
    def df(self):
        return get_data(self.ticker1, self.ticker2)


# The following code adds a "/bokeh/model_dashboard/" url to the bokeh-server. This URL
# will render this TopikApp. If you don't want serve this applet from a Bokeh
# server (for instance if you are embedding in a separate Flask application),
# then just remove this block of code.
@bokeh_app.route("/bokeh/model_dashboard/")
@object_page("model_dashboard")
def make_dashboard():
    app = TopikApp.create()
    return app
