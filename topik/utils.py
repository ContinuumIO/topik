import json
import logging
import os

import gensim

import numpy as np
import pandas as pd


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def generate_csv_output_file(reader, tokenizer, corpus_bow, lda_model, output_file='output.csv'):
    """Utility function to retrieve the results of your topic modeling in a csv file.
    Uses a pandas.DataFrame, only useful for smaller datasets.

    Parameters
    ----------
    reader : topik.readers
    tokenizer : topik.tokenizer
    corpus_bow : topik.intermediares.digested_document_collection.DigestedDocumentCollection instance
    lda : topik.models.LDA instance
    output_file : string
        Desired name for your output file

    Returns
    -------
    pandas.DataFrame
        A pandas.DataFrame with fields:

            * `text`: The original text content of the document
            * `tokens`: The tokens extracted from the text
            * `lda_probabilities`: A list of topic number and probability of the document belonging to each of the topics.
            * `topic_group`: Topic with max. probability

    """
    logging.info("getting output file %s " %output_file)
    documents = []

    with open(output_file, 'w') as wfile:
        #for fullpath, content in reader:3
        for content in reader:
            document = {}
            document['text'] = content
            tokens = tokenizer.tokenize(content)
            document['tokens'] = tokens
            bow_document = corpus_bow.dict.doc2bow(tokens)
            document['lda_probabilities'] = lda_model[bow_document]
            document['topic_group'] =  max(lda_model[bow_document], key=lambda item: item[1])[0]
            wfile.write(json.dumps(document))
            wfile.write('\n')
            documents.append(document)

    df = pd.DataFrame(documents)
    logging.info("writing dataframe to output file %s " %output_file)
    df.to_csv(output_file, sep='\t', encoding='utf-8')
    return pd.DataFrame(documents)
