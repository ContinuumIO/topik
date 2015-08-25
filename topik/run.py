from __future__ import absolute_import, print_function

import logging
import os
import shutil
import subprocess
import time
import webbrowser

import numpy as np

from topik.readers import read_input, get_filtered_elastic_results
from topik.preprocessing import preprocess
from topik.models import LDA
from topik.viz import Termite
from topik.utils import to_r_ldavis, generate_csv_output_file


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def run_model(data_source, source_type="auto", es_index=None,
              tokenizer='simple', n_topics=10, dir_path='./topic_model',
              model='lda_batch', termite_plot=True, output_file=False,
              r_ldavis=False, prefix_value=None, event_value=None,
              content_field=None, year_field=None, start_year=None,
              stop_year=None, seed=42, destination_es_instance=None,
              destination_es_index=None, id_field=None, clear_es_index=False,
              **kwargs):
    """Run your data through all topik functionality and save all results to a specified directory.

    Parameters
    ----------
    data: string
        Input data (e.g. file or folder or solr/elasticsearch instance).

    format: {'json_stream', 'folder_files', 'json_large', 'solr', 'elastic'}.
        The format of your data input. Currently available a json stream or a folder containing text files.
        Default is 'json_stream'

    tokenizer: {'simple', 'collocations', 'entities', 'mixed'}
        The type of tokenizer to use. Default is 'simple'.

    n_topics: int
        Number of topics to find in your data

    dir_path: string
        Directory path to store all topic modeling results files. Default is `./topic_model`.

    model: {'lda_batch', 'lda_online'}.
        Statistical modeling algorithm to use. Default 'lda_batch'.

    termite_plot: bool
        Generate termite plot of your model if True. Default is True.

    output_file: bool
        Generate a final summary csv file of your results. For each document: text, tokens, lda_probabilities and topic.

    r_ldavis: bool
        Generate an interactive data visualization of your topics. Default is False.

    prefix_value: string
        For 'large json' format reader, the prefix value to parse.

    event_value: string
        For 'large json' format reader, the event value to parse.

    content_field: string
        For 'json_stream', 'solr' or 'elastic' format readers, the field to parse.

    year_field: string
        For 'json_stream', 'solr' or 'elastic' format readers, the field containing year of publicaiton (for filtering).

    start_year: int
        For beginning of range filter on year_field values

    stop_year: int
        For beginning of range filter on year_field values

    destination_es_instance: string
        The address of the intermediate elasticsearch instance

    destination_es_index: string
        The index to use within the intermediate elasticsearch instance

    solr_query: string
        For 'solr' format reader, an optional query. Default is '*:*' to retrieve all documents.

    es_query:
        For 'elastic' format reader, an optional query. Default is None to retrieve all documents.
    seed: int
        Set random number generator to seed, to be able to reproduce results. Default 42.


    """
    np.random.seed(seed)

    raw_data = read_input(data_source, content_field=content_field,
                          source_type=source_type, **kwargs)
    processed_data = preprocess(raw_data, tokenizer_method=tokenizer, **kwargs)

    # Serialize and store the corpus
    # Create LDA model from corpus and dictionary
    if model == 'lda_batch':
        # To perform lda in batch mode set update_every=0 and passes=20)
        # https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation
        lda = LDA(processed_data, n_topics, update_every=0, passes=20)
    elif model == 'lda_online':
        # To perform lda in online mode set variables update_every, chunksize and passes.
        lda = LDA(processed_data, n_topics, update_every=1,
                  chunksize=10000, passes=1)
    else:
        logging.warning('model provided not valid. Using lda_batch.')
        lda = LDA(processed_data, n_topics, update_every=0, passes=20)
    # Get termite plot for this model
    if termite_plot:
        # Generate the input for the termite plot
        csv_path = os.path.join(dir_path, 'termite.csv')
        lda.termite_data(csv_path)
        termite = Termite(csv_path, "Termite Plot")
        termite.plot(os.path.join(dir_path, 'termite.html'))

    if output_file:
        filtered_documents = get_filtered_elastic_results(
            destination_es_instance, destination_es_index, content_field,
            year_field, start_year, stop_year)
        df_results = generate_csv_output_file(filtered_documents, raw_data,
                                              processed_data, lda.model)

    if r_ldavis:
        to_r_ldavis(processed_data, dir_name=os.path.join(dir_path, 'ldavis'), lda=lda)
        os.environ["LDAVIS_DIR"] = os.path.join(dir_path, 'ldavis')
        try:
            subprocess.call(['Rscript', os.path.join(BASEDIR, 'R/runLDAvis.R')])
        except ValueError:
            logging.warning("Unable to run runLDAvis.R")
        os.chdir(os.path.join(dir_path, 'ldavis', 'output'))
        sp = subprocess.Popen(['python', '-m', 'SimpleHTTPServer', '8000'])
        webbrowser.open_new_tab('127.0.0.1:8000')
        time.sleep(30)
        sp.kill()
