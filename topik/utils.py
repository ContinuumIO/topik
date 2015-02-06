import itertools
import logging
import re
import os
import json

from textblob import TextBlob
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
import numpy as np
import pandas as pd
import gensim

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def head(stream, n=1):
    """
    Return the first 'n' elements of a stream as plain list.

    Parameters
    ----------
    stream: iterable object
        The iterable where to get the first 'n' elements

    n: int
        Number of first elements to retrieve
    """
    return list(itertools.islice(stream, n))


def collocations(stream, top_n=10000, min_bigram_freq=50, min_trigram_freq=20):
    """
    Extract text collocations (bigrams and trigrams), from a stream of words.

    Parameters
    ----------
    stream: iterable object
        An iterable of words

    top_n: int
        Number of collocations to retrieve from the stream of words (order by decreasing frequency). Default is 10000

    min_bigram_freq: int
        Minimum frequency of a bigram in order to retrieve it. Default is 50.

    min_trigram_freq: int
        Minimum frequency of a trigram in order to retrieve it. Default is 20.

    """
    tcf = TrigramCollocationFinder.from_words(stream)

    tcf.apply_freq_filter(min_trigram_freq)
    trigrams = [' '.join(w) for w in tcf.nbest(TrigramAssocMeasures.chi_sq, top_n)]
    logging.info("%i trigrams found: %s..." % (len(trigrams), trigrams[:20]))

    bcf = tcf.bigram_finder()
    bcf.apply_freq_filter(min_bigram_freq)
    bigrams = [' '.join(w) for w in bcf.nbest(BigramAssocMeasures.pmi, top_n)]
    logging.info("%i bigrams found: %s..." % (len(bigrams), bigrams[:20]))

    bigrams_patterns = re.compile('(%s)' % '|'.join(bigrams), re.UNICODE)
    trigrams_patterns = re.compile('(%s)' % '|'.join(trigrams), re.UNICODE)

    return bigrams_patterns, trigrams_patterns



def entities(document_stream, freq_min=2, freq_max=10000):
    """
    Return noun phrases from stream of documents.

    Parameters
    ----------

    document_stream: iterable object

    freq_min: int
        Minimum frequency of a noun phrase occurrences in order to retrieve it. Default is 2.

    freq_max: int
        Maximum frequency of a noun phrase occurrences in order to retrieve it. Default is 10000.

    """
    np_counts_total = {}
    for docno, doc in enumerate(document_stream):
        if docno % 1000 == 0:
            sorted_phrases = sorted(np_counts_total.iteritems(), key=lambda item: -item[1])
            np_counts_total = dict(sorted_phrases)
            logging.info("at document #%i, considering %i phrases: %s..." %
                         (docno, len(np_counts_total), head(sorted_phrases)))

        for np in TextBlob(doc).noun_phrases:
            np_counts_total[np] = np_counts_total.get(np, 0) + 1

    # Remove noun phrases in the list that have higher frequencies than 'freq_max' or lower frequencies than 'freq_min'
    np_counts = {}
    for np, count in np_counts_total.iteritems():
        if count <= freq_max and count >= freq_min:
            np_counts[np] = count

    return set(np_counts)


def get_document_length(corpus_bow, folder):
    corpus_file = corpus_bow.filename
    corpus = gensim.corpora.MmCorpus(corpus_file)
    doc_length = []
    with open(os.path.join(folder, 'doc_length'), 'w') as f:
        for document in corpus:
            n_tokens = len(document)
            doc_length.append(n_tokens)
            f.write("%s\n" % n_tokens)

    return doc_length


def to_r_ldavis(corpus_bow, lda, dir_name):
    """
    Generate the input that the R package LDAvis needs.

    Parameters
    ----------
    corpus_bow: topik.vectorizers.CorpusBOW
        The corpus bag-of-words representation

    lda: topik.models.LDA
        LDA model

     dir_name: string
        Directory name where to store the files required in R package LDAvis.

    """

    if os.path.isfile(dir_name):
        pass
    else:
        os.makedirs(dir_name)
    doc_length = get_document_length(corpus_bow, dir_name)

    corpus_dict = corpus_bow.dict
    corpus_dict.save_as_text(os.path.join(dir_name,'dictionary'), sort_by_word=False)

    df = pd.read_csv(os.path.join(dir_name,'dictionary'), sep='\t', index_col=0, header=None)
    df = df.sort_index()

    df[2].to_csv(os.path.join(dir_name,'term_frequency'), index=False)
    df[1].to_csv(os.path.join(dir_name,'vocab'), index=False, header=False)

    tt_dist = np.array(lda.model.expElogbeta)
    np.savetxt(os.path.join(dir_name,'topicTermDist'), tt_dist)

    docTopicProbMat = lda.model[corpus_bow]
    gensim.corpora.MmCorpus.serialize(os.path.join(dir_name,'docTopicProbMat.mm'), docTopicProbMat)


def generate_csv_output_file(reader, tokenizer, corpus_bow, lda_model, output_file='output.csv'):
    """
    Utility function to retrieve the results of your topic modeling in a csv file.
    Uses a pandas.DataFrame, only useful for smaller datasets.

    Parameters
    ----------
    reader: topik.readers
    tokenizer: topik.tokenizer
    corpus_bow: topik.vectorizer.CorpusBOW
    lda: topik.models.LDA
    output_file: string
        Desired name for your output file

    Returns
    -------
    pandas.DataFrame
        A pandas.DataFrame with fields:
            `text`: The original text content of the document
            `tokens`: The tokens extracted from the text
            `lda_probabilities`: A list of topic number and probability of the document belonging to each of the topics.
            `topic_group`: Topic with max. probability

    """
    iter = itertools.tee(reader, 1)
    logging.info("getting output file %s " %output_file)
    documents = []

    with open(output_file, 'w') as wfile:
        for content in iter:
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