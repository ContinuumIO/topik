from __future__ import absolute_import

import os
import subprocess
import logging

from topik.readers import iter_document_json_stream, iter_documents_folder
from topik.tokenizers import SimpleTokenizer, CollocationsTokenizer, EntitiesTokenizer, MixedTokenizer
from topik.vectorizers import CorpusBOW
from topik.models import LDA
from topik.viz import Termite
from topik.utils import to_r_ldavis, generate_csv_output_file


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def run_topic_modeling(data, format='json_stream', tokenizer='simple', n_topics=10, dir_path='topic_model',
                       termite_plot=True, output_file=False, r_ldavis=False):
    """
    Run your data through all topik functionality and save all results to a specified directory.

    Parameters
    ----------
    data: string
        Input data (file or folder).

    format: {'json_stream', 'folder_files'}.
        The format of your data input. Currently available a json stream or a folder containing text files. 
        Default is 'json_stream'

    tokenizer: {'simple', 'collocations', 'entities', 'mixed'}
        The type of tokenizer to use. Default is 'simple'.
    
    n_topics: int
        Number of topics to find in your data
        
    dir_path: string
        Directory path to store all topic modeling results files. Default is `topic_model`.

    termite_plot: bool
        Generate termite plot of your model if True. Default is True

    output_file: bool
        Generate a final summary csv file of your results. For each document: text, tokens, lda_probabilities and topic.

    r_ldavis:
        Generate an interactive data visualization of your topics.
    """
    if format == 'folder_files':
        documents = iter_documents_folder(data)
    else:
        documents = iter_document_json_stream(data)

    if tokenizer == 'simple':
        corpus = SimpleTokenizer(documents)
    elif tokenizer == 'collocations' :
        corpus = CollocationsTokenizer(documents)
    elif tokenizer == 'entities':
        corpus = EntitiesTokenizer(documents)
    elif tokenizer == 'mixed':
        corpus = MixedTokenizer(documents)
    else:
        print("Processing value invalid, using 1-Simple by default")
        corpus = SimpleTokenizer(documents)

    os.makedirs(dir_path)

    # Create dictionary
    corpus_bow = CorpusBOW(corpus)
    corpus_dict = corpus_bow.save_dict(os.path.join(dir_path, 'corpus.dict'))
    # Serialize and store the corpus
    corpus_bow.serialize(os.path.join(dir_path, 'corpus.mm'))
    # Create LDA model from corpus and dictionary
    lda = LDA(os.path.join(dir_path, 'corpus.mm'), os.dir_path.join(dir_path,'corpus.dict'), n_topics)
    # Generate the input for the termite plot
    lda.termite_data(os.path.join(dir_path,'termite.csv'))
    # Get termite plot for this model
    if termite_plot:
        termite = Termite(os.path.join(dir_path,'termite.csv'), "Termite Plot")
        termite.plot(os.path.join(dir_path,'termite.html'))

    if output_file:
        df_results = generate_csv_output_file(documents, corpus, corpus_bow, lda.model)

    #WIP
    #if r_ldavis:
    #    to_r_ldavis(corpus_bow, dir_name=dir_path, lda=lda)
    #    os.chdir(dir_path)
    #    try:
    #        subprocess.call(['R'])
    #    except ValueError:
    #        logging.warning("Unable to run runLDAvis.R")


