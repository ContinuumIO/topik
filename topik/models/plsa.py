# -*- coding: utf-8 -*-

import logging
import math
import operator
import random

import numpy as np
import pandas as pd

from .model_base import TopicModelBase, register_model
from topik.intermediaries.raw_data import load_persisted_corpus


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


# def _rand_mat(sizex, sizey):
#     ret = []
#     for i in xrange(sizex):
#         ret.append([])
#         for _ in xrange(sizey):
#             ret[-1].append(random.random())
#         norm = sum(ret[-1])
#         for j in xrange(sizey):
#             ret[-1][j] /= norm
#     return ret

def _rand_mat(cols, rows):
    out = np.random.random((rows, cols))
    for row in out:
        row /= row.sum()
    return out


@register_model
class PLSA(TopicModelBase):
    def __init__(self, corpus=None, ntopics=2, load_filename=None, binary_filename=None):
        # corpus comes in as a list of lists of tuples.  Each inner list represents a document, while each
        #     tuple contains (id, count) of words in that document.
        self.topics = ntopics
        self.topic_array = np.arange(ntopics, dtype=np.int32)
        if corpus:
            # iterable, each entry is tuple of (word_id, count)
            self._corpus = corpus
            # total number of identified words for each given document (document length normalization factor?)
            self.each = map(sum, map(lambda x: x[1], corpus))
            # Maximum identified word (number of identified words in corpus)
            # TODO: seems like this could be tracked better during the tokenization step and fed in.
            self.words = len(corpus._dict.token2id)
            self.likelihood = 0
            # topic-word matrix
            self.zw = _rand_mat(self.words, self.topics)
            # document-topic matrix
            self.dz = _rand_mat(self.topics, len(corpus))
            self.dw_z = [{}, ] * len(corpus)
            self.p_dw = [{}, ] * len(corpus)
            self.beta = 0.8
        elif load_filename and binary_filename:
            from topik.intermediaries.digested_document_collection import DigestedDocumentCollection
            self._corpus = DigestedDocumentCollection(load_persisted_corpus(load_filename))
            # total number of identified words for each given document (document length normalization factor?)
            self.each = map(sum, map(lambda x: x[1], self._corpus))
            # Maximum identified word (number of identified words in corpus)
            # TODO: seems like this could be tracked better during the tokenization step and fed in.
            self.words = max(reduce(operator.add, map(lambda x: x[0], self._corpus)))+1
            arrays = np.load(binary_filename)
            self.zw = arrays['zw']
            self.dz = arrays['dz']
            self.dw_z = arrays['dw_z']
            self.p_dw = arrays['p_dw']
            self.beta, self.likelihood = arrays["beta_likelihood"]
        else:
            pass  # is just being used for inference

    def save(self, filename):
        np.savez_compressed(self.get_model_name_with_parameters(),
                            zw=self.zw,
                            dz=self.dz,
                            dw_z=self.dw_z,
                            p_dw=self.p_dw,
                            beta_likelihood=np.array([self.beta, self.likelihood]))
        saved_data = {"load_filename": filename, "binary_filename": self.get_model_name_with_parameters()+".npz"}
        super(PLSA, self).save(filename, saved_data=saved_data)

    def get_model_name_with_parameters(self):
        return "PLSA_{}_topics{}".format(self.topics, self._corpus.filter_string)

    def _cal_p_dw(self):
        for d, doc in enumerate(self._corpus):
            for word_id, word_ct in doc:
                tmp = 0
                for _ in range(word_ct):
                    for z in self.topic_array:
                        tmp += (self.zw[z][word_id]*self.dz[d][z])**self.beta
                self.p_dw[-1][word_id] = tmp

    def _e_step(self):
        self._cal_p_dw()
        for d, doc in enumerate(self._corpus):
            for word_id, word_ct in doc:
                self.dw_z[-1][word_id] = []
                for z in self.topic_array:
                    self.dw_z[-1][word_id].append(((self.zw[z][word_id]*self.dz[d][z])**self.beta)/self.p_dw[d][word_id])

    def _m_step(self):
        for z in self.topic_array:
            self.zw[z] = [0]*self.words
            for d, doc in enumerate(self._corpus):
                for word_id, word_ct in doc:
                    self.zw[z][word_id] += word_ct*self.dw_z[d][word_id][z]
            norm = sum(self.zw[z])
            for w in xrange(self.words):
                self.zw[z][w] /= norm
        for d, doc in enumerate(self._corpus):
            self.dz[d] = 0
            for z in self.topic_array:
                for word_id, word_ct in doc:
                    self.dz[d][z] += word_ct * self.dw_z[d][word_id][z]
            for z in self.topic_array:
                self.dz[d][z] /= self.each[d]

    def _cal_likelihood(self):
        self.likelihood = 0
        for d, doc in enumerate(self._corpus):
            for word_id, word_ct in doc:
                self.likelihood += word_ct*math.log(self.p_dw[d][word_id])

    def train(self, max_iter=100):
        cur = 0
        for i in xrange(max_iter):
            logging.info('%d iter' % i)
            self._e_step()
            self._m_step()
            self._cal_likelihood()
            logging.info('likelihood %f ' % self.likelihood)
            if cur != 0 and abs((self.likelihood-cur)/cur) < 1e-8:
                break
            cur = self.likelihood

    def inference(self, doc, max_iter=100):
        doc = dict(filter(lambda x: x[0] < self.words, doc.items()))
        words = sum(doc.values())
        ret = []
        for i in xrange(self.topics):
            ret.append(random.random())
        norm = sum(ret)
        for i in xrange(self.topics):
            ret[i] /= norm
        tmp = 0
        for _ in xrange(max_iter):
            p_dw = {}
            for w in doc:
                p_dw[w] = 0
                for _ in range(doc[w]):
                    for z in xrange(self.topics):
                        p_dw[w] += (ret[z]*self.zw[z][w])**self.beta
            # e setp
            dw_z = {}
            for w in doc:
                dw_z[w] = []
                for z in xrange(self.topics):
                    dw_z[w].append(((self.zw[z][w]*ret[z])**self.beta)/p_dw[w])
            logging.debug('inference dw_z %r' % (dw_z,))
            # m step

            ret = [0]*self.topics
            for z in xrange(self.topics):
                for w in doc:
                    ret[z] += doc[w]*dw_z[w][z]
            for z in xrange(self.topics):
                ret[z] /= words
            # cal likelihood
            likelihood = 0
            for w in doc:
                likelihood += doc[w]*math.log(p_dw[w])
            if tmp != 0 and abs((likelihood-tmp)/tmp) < 1e-8:
                break
            tmp = likelihood
        return (ret, likelihood)

    def post_prob_sim(self, docd, q):
        sim = 0
        for w in docd:
            tmp = 0
            for z in xrange(self.topics):
                tmp += self.zw[z][w]*q[z]
            sim += docd[w]*math.log(tmp)
        return sim

    def get_top_words(self, topn):
        top_words = []
        # each "topic" is a row of the dz matrix
        for topic in self.dz.T:
            word_ids = np.argpartition(topic, -topn)[-topn:]
            word_ids = reversed(word_ids[np.argsort(topic[word_ids])])
            top_words.append([(topic[word_id], self._corpus.get_id2word_dict()[word_id]) for word_id in word_ids])
        return top_words

    def _get_topic_term_dists(self):
        term_topic_df = pd.DataFrame(self.zw,
                            index=['topic'+str(t)+'dist' for t in range(self.topics)]).T

        term_topic_df.index.name = 'term_id'
        return term_topic_df

    def _get_doc_topic_dists(self):
        doc_topic_df = pd.DataFrame(self.dz,
                            index=[doc[0] for doc in self._corpus._corpus],
                            columns=['topic'+str(t)+'dist' for t in range(self.topics)])

        doc_topic_df.index.name = 'doc_id'
        return doc_topic_df
