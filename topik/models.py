from __future__ import absolute_import

import logging

import gensim
import pandas as pd

# imports used only for doctests
from topik.readers import read_input
from topik.tests import test_data_path
from topik.preprocessing import preprocess


class LDA(object):
    """A high interface for an LDA (Latent Dirichlet Allocation) model.

    Parameters
    ----------
    corpus_file: string
        Location of the corpus serialized in Matrix Market format
    dict_file: string
        Location of the dictionary

    >>> raw_data = read_input(
                    '{}/test_data_json_stream.json'.format(test_data_path),
                    content_field="abstract")
    >>> processed_data = preprocess(raw_data)
    >>> my_lda = LDA(processed_data)

    """
    def __init__(self, corpus_file, dict_file, ntopics=10, **kwargs):
        self.corpus = gensim.corpora.MmCorpus(corpus_file)
        self.dictionary = gensim.corpora.Dictionary.load(dict_file)
        self.model = gensim.models.LdaModel(self.corpus, num_topics=ntopics, id2word=self.dictionary, **kwargs)

    def save(self, filename):
        self.model.save(filename)

    def get_top_words(self, topn):
        top_words = [self.model.show_topic(topicno, topn) for topicno in range(self.model.num_topics)]
        return top_words

    def termite_data(self, filename="termite.csv", topn_words=15):
        """Generate the csv file input for the termite plot.

        Parameters
        ----------
        filename: string
            Desired name for the generated csv file
        >>> raw_data = read_input(
                        '{}/test_data_json_stream.json'.format(test_data_path),
                        content_field="text")
        >>> processed_data = preprocess(raw_data)
        >>> my_lda = LDA(processed_data)
        >>> my_lda.termite_data('termite.csv', 15)

        """
        logging.info("generating termite plot input from %s " % self.corpus)
        top_words = self.get_top_words(topn_words)
        count = 1
        for topic in top_words:
            if count == 1:
                df_temp = pd.DataFrame(topic, columns=['weight', 'word'])
                df_temp['topic'] = pd.Series(count, index=df_temp.index)
                df = df_temp
            else:
                df_temp = pd.DataFrame(topic, columns=['weight', 'word'])
                df_temp['topic'] = pd.Series(count, index=df_temp.index)
                df = df.append(df_temp, ignore_index=True)
            count += 1
        logging.info("saving termite plot input csv file to %s " % filename)
        df.to_csv(filename, index=False, encoding='utf-8')
        return df
