import numpy as np
import pandas as pd

from bokeh.plotting import figure, curdoc, vplot, output_file, show
from bokeh.embed import autoload_server, components
from bokeh.client import push_session
from bokeh.models import Button, ColumnDataSource


def topic_cluster(data):
    output_file("topic_cluster.html")

    plot = figure()
    xcoords = data["x"]
    ycoords = data["y"]
    frequency = data["Freq"]
    for x, y, size in zip(xcoords, ycoords, frequency):
        plot.circle(x, y, size=(size*7), alpha=0.5)

    # curdoc().add_root(plot)
    # session = push_session(curdoc())
    # script = autoload_server(model=None, session_id=session.id)
    # return script
    show(plot)


def word_frequency(data):
    factors = ["a", "b", "c", "d", "e", "f", "g", "h"]
    x =  [50, 40, 65, 10, 25, 37, 80, 60]
    output_file("word_frequency.html")
    plot = figure(y_range=factors, x_range=[0,100])
    plot.segment(0, factors, x, factors, line_width=10, line_color="green")
    show(plot)
