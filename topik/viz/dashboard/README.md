This Bokeh applet can be viewed in two different ways:

* running directly on a bokeh-server
* embedded into a separate Flask application

Running
=======

Bokeh Server
------------

To view this applet directly from a bokeh server, you simply need to
run a bokeh-server and point it at the topik_app script:

    bokeh-server --script topik_app.py

Now navigate to the following URL in a browser:

    http://localhost:5006/bokeh/topik

Flask Application
-----------------

To embed this applet into a Flask application, first you need to run
a bokeh-server and point it at the topik_app script. In this
directory, execute the command:

    bokeh-server --script topik_app.py

Next you need to run the flask server that embeds the applet:

    python flask_server.py

Now you can see the stock correlation applet by navigating to the following
URL in a browser:

    http://localhost:5050/
