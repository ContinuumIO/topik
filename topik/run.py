from __future__ import absolute_import, print_function

import logging
import os
import subprocess
import time
import webbrowser

import numpy as np

from topik.readers import read_input
import topik.models
from topik.viz import plot_lda_vis, Termite


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def run_model(data_source, source_type="auto", year_field=None, start_year=None, stop_year=None,
              content_field=None, tokenizer='simple', n_topics=10, dir_path='./topic_model', model='LDA',
              termite_plot=True, output_file=False, ldavis=False, seed=42, **kwargs):

    """Run your data through all topik functionality and save all results to a specified directory.

    Parameters
    ----------
    data_source : str
        Input data (e.g. file or folder or solr/elasticsearch instance).

    source_type : {'json_stream', 'folder_files', 'json_large', 'solr', 'elastic'}.
        The format of your data input. Currently available a json stream or a folder containing text files.
        Default is 'json_stream'
    year_field : str
        The field name (if any) that contains the year associated with each document (for filtering).
    start_year : int
        For beginning of range filter on year_field values
    stop_year : int
        For beginning of range filter on year_field values
    content_field : string
        The primary text field to parse.
    tokenizer : {'simple', 'collocations', 'entities', 'mixed'}
        The type of tokenizer to use. Default is 'simple'.
    n_topics : int
        Number of topics to find in your data
    dir_path : str
        Directory path to store all topic modeling results files. Default is `./topic_model`.
    model : {'LDA', 'PLSA'}.
        Statistical modeling algorithm to use. Default 'LDA'.
    termite_plot : bool
        Generate termite plot of your model if True. Default is True.
    output_file : bool
        Generate a final summary csv file of your results. For each document: text, tokens, lda_probabilities and topic.
    ldavis : bool
        Generate an interactive data visualization of your topics. Default is False.
    seed : int
        Set random number generator to seed, to be able to reproduce results. Default 42.
    **kwargs : additional keyword arguments, passed through to each individual step
    """

    np.random.seed(seed)

    raw_data = read_input(data_source, content_field=content_field,
                          source_type=source_type, **kwargs)
    processed_data = raw_data.tokenize(method=tokenizer, **kwargs)
    model = topik.models.registered_models[model](processed_data, n_topics, **kwargs)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    if termite_plot:
        termite = Termite(model.termite_data(n_topics), "Termite Plot")
        termite.plot(os.path.join(dir_path, 'termite.html'))

    if ldavis:
        plot_lda_vis(model.to_py_lda_vis())


