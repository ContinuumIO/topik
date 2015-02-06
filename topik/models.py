from __future__ import absolute_import

import logging

import gensim
import pandas as pd


class LDA(object):
    """
    A high interface for an LDA (Latent Dirichlet Allocation) model.

    Parameters
    ----------
    corpus_file: string
        Location of the corpus serialized in Matrix Market format
    dict_file: string
        Location of the dictionary

    >>> my_lda = LDA("my_corpus.mm", "my_dict.dict")
    """

    def __init__(self, corpus_file, dict_file, ntopics=10, **kwargs):
        self.corpus = gensim.corpora.MmCorpus(corpus_file)
        self.dictionary = gensim.corpora.Dictionary.load(dict_file)
        self.model = gensim.models.LdaModel(self.corpus, num_topics=ntopics, id2word=self.dictionary, **kwargs)

    def save(self, filename):
        self.model.save(filename)

    def get_top_words(self, topn):
        top_words = [ self.model.show_topic(topicno, topn) for topicno in range(self.model.num_topics) ]
        return top_words

    def termite_data(self, filename="termite.csv", topn_words=15):
        """
        Generate the csv file input for the termite plot.

        Parameters
        ----------
        filename: string
            Desired name for the generated csv file
        >>> my_lda = LDA("my_corpus.mm", "my_dict.dict")
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
