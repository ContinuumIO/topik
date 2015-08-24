from __future__ import absolute_import, print_function

import os
import time
import subprocess
import logging
import shutil
import webbrowser

import numpy as np

from topik.readers import iter_document_json_stream, iter_documents_folder,\
        iter_large_json, iter_solr_query, iter_elastic_query,\
        reader_to_elastic, get_filtered_elastic_results
from topik.tokenizers import SimpleTokenizer, CollocationsTokenizer, EntitiesTokenizer, MixedTokenizer
from topik.vectorizers import CorpusBOW
from topik.models import LDA
from topik.viz import Termite
from topik.utils import to_r_ldavis, generate_csv_output_file, unzip


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def run_model(data, es_index=None, format='json_stream', tokenizer='simple', n_topics=10, dir_path='./topic_model',
                    model='lda_batch', termite_plot=True, output_file=False, r_ldavis=False,  
                    prefix_value=None, event_value=None, content_field=None, year_field=None,
                    start_year=None, stop_year=None, es_query=None, solr_query='*:*', subfield=None, seed=42,
                    destination_es_instance=None, destination_es_index=None, id_field=None,
                    clear_es_index=False):
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

    # TODO: replace all prints with logging
    """
    ====================================================================
    STEP 1: Read all documents from source and yield full-featured dicts
    ====================================================================
    """

    print("Beginning STEP 1: Reading documents from source")

    if format == 'folder_files':
        documents = iter_documents_folder(data, content_field)
    elif format == 'json_stream' and content_field is not None:
        documents = iter_document_json_stream(data, year_field)
    elif format == 'large_json' and content_field is not None:
        documents = iter_large_json(data, year_field, id_field, prefix_value)
    elif format == 'solr' and content_field is not None:
        id_documents = iter_solr_query(data, content_field, query=solr_query)
    elif format == 'elastic' and content_field is not None:
        documents = iter_elastic_query(data, es_index, query=es_query)
    else:
        raise Exception("Invalid input, make sure your passing the appropriate arguments for the different formats")


    print("STEP 1 Complete")

    """
    ====================================================================
    STEP 2: Load dicts from reader-generator into elasticsearch instance
    ====================================================================
    """

    print("Beginning STEP 2: Loading documents into elasticsearch")
    
    reader_to_elastic(destination_es_instance,
                   destination_es_index, documents, clear_es_index)

    print("STEP 2 Complete")

    """
    ===========================================================
    STEP 3: Get year-filtered documents back from elasticsearch
    ===========================================================
    """

    print("Beginning STEP 3: fetching documents from elasticsearch")

    filtered_documents = get_filtered_elastic_results(destination_es_instance,
                            destination_es_index, content_field,
                            year_field, start_year, stop_year)


    #for i, doc in enumerate(filtered_documents):
    #    print(str(i) + ':' + doc + ',')
        
    print("STEP 3 Complete")
    
    """
    ===========================================================
    STEP 4: For each document, Tokenize the raw text body into
            a list of words
    ===========================================================
    """

    print("Beginning STEP 4: Tokenization")

    if tokenizer == 'simple':
        corpus = SimpleTokenizer(filtered_documents)
    elif tokenizer == 'collocations' :
        corpus = CollocationsTokenizer(filtered_documents)
    elif tokenizer == 'entities':
        corpus = EntitiesTokenizer(filtered_documents)
    elif tokenizer == 'mixed':
        corpus = MixedTokenizer(filtered_documents)
    else:
        print("Processing value invalid, using simple")
        corpus = SimpleTokenizer(filtered_documents)

    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

    os.makedirs(dir_path)
    

    #for i, c in enumerate(corpus):
    #    print(i)
    #    print(c)
    
    
    print("STEP 4 Complete")

    """
    ===========================================================
    STEP 5: For each document, Vectorize the list of words into
            a Bag of Words (or N-grams?)
    ===========================================================
    """

    print("Beginning STEP 5: Vectorization")

    # Create dictionary
    corpus_bow = CorpusBOW(corpus)
    # Serialize and store the corpus
    # Create LDA model from corpus and dictionary
    if model == 'lda_batch':
        # To perform lda in batch mode set update_every=0 and passes=20)
        # https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation
        lda = LDA(corpus_input, n_topics, update_every=0, passes=20)
    elif model == 'lda_online':
        # To perform lda in online mode set variables update_every, chuncksize and passes.
        lda = LDA(corpus_input, n_topics, update_every=1, chunksize=10000, passes=1)
    else:
        logging.warning('model provided not valid. Using lda_batch.')
        lda = LDA(corpus_input, n_topics, update_every=0, passes=20)
    # Get termite plot for this model
    if termite_plot:
        # Generate the input for the termite plot
        lda.termite_data(os.path.join(dir_path,'termite.csv'))
        termite = Termite(os.path.join(dir_path,'termite.csv'), "Termite Plot")
        termite.plot(os.path.join(dir_path,'termite.html'))


    if output_file:

        filtered_documents = get_filtered_elastic_results(destination_es_instance,
                        destination_es_index, content_field,
                        year_field, start_year, stop_year)
        df_results = generate_csv_output_file(filtered_documents, corpus, corpus_bow, lda.model)
    

    if r_ldavis:
        to_r_ldavis(corpus_bow, dir_name=os.path.join(dir_path, 'ldavis'), lda=lda)
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
