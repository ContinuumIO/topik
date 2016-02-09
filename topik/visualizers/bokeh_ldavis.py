import numpy as np
import pandas as pd

from bokeh.plotting import figure, curdoc, vplot, output_file, show
from bokeh.embed import autoload_server, components
from bokeh.client import push_session
from bokeh.models import Button, ColumnDataSource


def bokeh_lda_vis(data=None):
    output_file("circles.html")

    plot = figure()
    xcoords = data["x"]
    ycoords = data["y"]
    frequency = data["Freq"]
    for x, y, size in zip(xcoords, ycoords, frequency):
        plot.circle(x, y, size=(size*2))

    # curdoc().add_root(plot)
    # session = push_session(curdoc())
    # script = autoload_server(model=None, session_id=session.id)
    # return script
    show(plot)


data = pd.read_json("sample.json")
bokeh_lda_vis(data)
