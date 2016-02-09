from urlparse import urlparse
from collections import Counter
import datetime
from operator import itemgetter

import numpy as np
import pandas as pd

from bokeh.plotting import figure, curdoc, vplot
from bokeh.embed import autoload_server, components
from bokeh.client import push_session
from bokeh.models import Button, ColumnDataSource


def pages_timeseries(response):
    parse_datetime = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")
    parsed_dates = [parse_datetime(x[1]) for x in response]
    dates = sorted(parsed_dates)
    plot = figure(plot_width=584, x_axis_type="datetime", x_axis_label="Dates",
            y_axis_label="Number Fetched")
    plot.line(x=dates, y=range(len(dates)))

    button = Button(label="Press Me")

    session = push_session(curdoc())
    script = autoload_server(vplot(plot, button), session_id=session.id)
    return script


def add_line():
    print("Clicked!")


def line_scratch():

    line_width = 4

    line1 = [(0, 1, 2, 3, 4, 5), (0, 1, 2, 3, 4, 5)]
    line2 = [(0, 1, 2, 3, 4, 5), (0, 5, 1, 4, 2, 3)]
    line3 = [(5, 4, 3, 2, 1), (5, 4, 3, 2, 1)]

    plot = figure()
    red = plot.line(x=line1[0], y=line1[1], line_width=line_width, color="crimson")
    blue = plot.line(x=line2[0], y=line2[1], line_width=line_width)
    # purple = plot.line(x=line3[0], y=line3[1], line_width=line_width, color="purple")

    button = Button(label="Add Line")
    button.on_click(add_line)

    curdoc().add_root(vplot(plot, button))
    session = push_session(curdoc())

    script = autoload_server(model=None, session_id=session.id)

    # script, div = components(vplot(plot, button))
    return script

line_scratch()
