from __future__ import absolute_import, print_function

import logging
import os
import numpy as np

from stop_words import get_stop_words
from topik.fileio import read_input
from topik import tokenizers, vectorizers, models, visualizers
from topik.visualizers.termite_plot import termite_html

BASEDIR = os.path.abspath(os.path.dirname(__file__))

def run_pipeline(data_source, source_type="auto", year_field=None, start_year=None, stop_year=None,
              content_field=None, tokenizer='simple', vectorizer='bag_of_words', ntopics=10,
              dir_path='./topic_model', model='lda', termite_plot=False, output_file=False,
              lda_vis=True, seed=42, **kwargs):



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
    tokenizer : {'simple', 'entities', 'mixed', 'ngrams'}
        The type of tokenizer to use. Default is 'simple'.
    vectorizer : {'bag_of_words', 'tfidf'}
        The type of vectorizer to use.  Default is 'bag_of_words'.
    ntopics : int
        Number of topics to find in your data
    dir_path : str
        Directory path to store all topic modeling results files. Default is `./topic_model`.
    model : {'LDA', 'PLSA'}.
        Statistical modeling algorithm to use. Default 'LDA'.
    termite_plot : bool
        Generate termite plot of your model if True. Default is True.
    ldavis : bool
        Generate an interactive data visualization of your topics. Default is False.
    seed : int
        Set random number generator to seed, to be able to reproduce results. Default 42.
    **kwargs : additional keyword arguments, passed through to each individual step
    """

    stopwords = get_stop_words("en")
    np.random.seed(seed)
    logging.info("Loading data as {} from {}".format(source_type, data_source))
    raw_data = read_input(data_source, content_field=content_field,
                          source_type=source_type, **kwargs)
    raw_data = ((hash(item[content_field]), item[content_field]) for item in raw_data)
    logging.info("Tokenizing data with {}".format(tokenizer))
    tokenized_data = tokenizers.registered_tokenizers[tokenizer](raw_data, stopwords=stopwords, **kwargs)
    logging.info("Vectorizing data with {}".format(vectorizer))
    vectorized_data = vectorizers.registered_vectorizers[vectorizer](tokenized_data, **kwargs)
    model = models.registered_models[model](vectorized_data, ntopics=ntopics, **kwargs)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    if termite_plot:
        termite_html(model, filename="termite.html", plot_title="Termite plot", topn=15)

    if lda_vis:
        visualizers.visualize(model, "lda_vis")


