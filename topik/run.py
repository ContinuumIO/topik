from __future__ import absolute_import

import os
import time
import subprocess
import logging
import shutil
import webbrowser

import numpy as np

from topik.readers import iter_document_json_stream, iter_documents_folder,\
        iter_large_json, iter_solr_query, iter_elastic_query
from topik.tokenizers import SimpleTokenizer, CollocationsTokenizer, EntitiesTokenizer, MixedTokenizer
from topik.vectorizers import CorpusBOW
from topik.models import LDA
from topik.viz import Termite
from topik.utils import to_r_ldavis, generate_csv_output_file, unzip


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def run_model(data, format='json_stream', tokenizer='simple', n_topics=10, dir_path='./topic_model',
                    model='lda_batch', termite_plot=True, output_file=False, r_ldavis=False,  prefix_value=None,
                    event_value=None, field=None, query='*:*', index=None, subfield=None, seed=42):
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

    field: string
        For 'json_stream', 'solr' or 'elastic' format readers, the field to parse.

    solr_instance: string
        For 'solr' format reader, the url to the solr instance.

    query: string
        For 'solr' format reader, an optional query. Default is '*:*' to retrieve all documents.

    seed: int
        Set random number generator to seed, to be able to reproduce results. Default 42.

    """
    np.random.seed(seed)

    if format == 'folder_files':
        id_documents = iter_documents_folder(data)
    elif format == 'large_json' and prefix_value is not None and event_value is not None:
        id_documents = iter_large_json(data, prefix_value, event_value)
    elif format == 'json_stream' and field is not None:
        id_documents = iter_document_json_stream(data, field)
    elif format == 'solr' and field is not None:
        id_documents = iter_solr_query(data, field, query=query)
    elif format == 'elastic' and field is not None:
        id_documents = iter_elastic_query(data, index, field, subfield)
    else:
        raise Exception("Invalid input, make sure your passing the appropriate arguments for the different formats")
    ids, documents = unzip(id_documents)

    if tokenizer == 'simple':
        corpus = SimpleTokenizer(documents)
    elif tokenizer == 'collocations' :
        corpus = CollocationsTokenizer(documents)
    elif tokenizer == 'entities':
        corpus = EntitiesTokenizer(documents)
    elif tokenizer == 'mixed':
        corpus = MixedTokenizer(documents)
    else:
        print("Processing value invalid, using simple")
        corpus = SimpleTokenizer(documents)

    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

    os.makedirs(dir_path)

    # Create dictionary
    corpus_bow = CorpusBOW(corpus)
    corpus_dict = corpus_bow.save_dict(os.path.join(dir_path, 'corpus.dict'))
    # Serialize and store the corpus
    corpus_file = corpus_bow.serialize(os.path.join(dir_path, 'corpus.mm'))
    # Create LDA model from corpus and dictionary
    if model == 'lda_batch':
        # To perform lda in batch mode set update_every=0 and passes=20)
        # https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation
        lda = LDA(os.path.join(dir_path, 'corpus.mm'), os.path.join(dir_path,'corpus.dict'), n_topics, update_every=0,
                  passes=20)
    elif model == 'lda_online':
        # To perform lda in online mode set variables update_every, chuncksize and passes.
        lda = LDA(os.path.join(dir_path, 'corpus.mm'), os.path.join(dir_path,'corpus.dict'), n_topics, update_every=1,
                  chuncksize=10000, passes=1)
    else:
        logging.warning('model provided not valid. Using lda_batch.')
        lda = LDA(os.path.join(dir_path, 'corpus.mm'), os.path.join(dir_path,'corpus.dict'), n_topics, update_every=0,
                  passes=20)
    # Generate the input for the termite plot
    lda.termite_data(os.path.join(dir_path,'termite.csv'))
    # Get termite plot for this model
    if termite_plot:
        termite = Termite(os.path.join(dir_path,'termite.csv'), "Termite Plot")
        termite.plot(os.path.join(dir_path,'termite.html'))

    if output_file:

        if format == 'folder_files':
            id_documents = iter_documents_folder(data)

        elif format == 'large_json':
            id_documents = iter_large_json(data, prefix_value, event_value)
        else:
            id_documents = iter_document_json_stream(data, field)

        ids, documents = unzip(id_documents)
        df_results = generate_csv_output_file(documents, corpus, corpus_bow, lda.model)

    if r_ldavis:
        to_r_ldavis(corpus_bow, dir_name=os.path.join(dir_path, 'ldavis'), lda=lda)
        os.environ["LDAVIS_DIR"] = os.path.join(dir_path, 'ldavis')
        try:
            subprocess.call(['Rscript', os.path.join(BASEDIR,'R/runLDAvis.R')])
        except ValueError:
            logging.warning("Unable to run runLDAvis.R")
        os.chdir(os.path.join(dir_path, 'ldavis', 'output'))
        sp = subprocess.Popen(['python', '-m', 'SimpleHTTPServer', '8000'])
        webbrowser.open_new_tab('127.0.0.1:8000')
        time.sleep(30)
        sp.kill()


