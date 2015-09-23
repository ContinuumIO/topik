"""
This file demonstrates embedding a bokeh applet into a flask
application. See the README.md file in this dirrectory for
instructions on running.
"""
from __future__ import print_function

import logging
logging.basicConfig(level=logging.INFO)

from bokeh.pluginutils import app_document
from flask import Flask, render_template

from topik_app import TopikApp

app = Flask('sampleapp')

bokeh_url = "http://localhost:5006"
applet_url = "http://localhost:5050"

@app_document("model_dashboard", bokeh_url)
def make_applet():
    app = TopikApp.create()
    return app

@app.route("/")
def applet():
    applet = make_applet()
    return render_template(
        "model_dashboard.html",
        app_url = bokeh_url + "/bokeh/jsgenerate/VBox/TopikApp/TopikApp",
        app_tag = applet._tag
    )

if __name__ == "__main__":
    print("\nView this example at: %s\n" % applet_url)
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
