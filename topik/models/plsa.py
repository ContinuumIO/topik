# -*- coding: utf-8 -*-

import gzip
import logging
import marshal
import math
import operator
import random
import sys

import numpy as np

from .model_base import TopicModelBase, register_model


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
    def __init__(self, corpus=None, topics=2, load_filename=None):
        # corpus comes in as a list of lists of tuples.  Each inner list represents a document, while each
        #     tuple contains (id, count) of words in that document.
        self.topics = topics
        if corpus:
            # iterable, each entry is tuple of (word_id, count)
            self.corpus = corpus
            self.docs = len(corpus)
            # total number of identified words for each given document (document length normalization factor?)
            self.each = map(sum, map(lambda x: x[1], corpus))
            # Maximum identified word (number of identified words in corpus)
            # TODO: seems like this could be tracked better during the tokenization step and fed in.
            self.words = max(reduce(operator.add, map(lambda x: x[0], corpus)))+1
            self.likelihood = 0
            # topic-word matrix
            self.zw = _rand_mat(self.topics, self.words)
            # document-topic matrix
            self.dz = _rand_mat(self.docs, self.topics)

            logging.debug('init self.zw %r self.dz %r' % (self.zw, self.dz))
            self.dw_z = None
            self.p_dw = []
            self.beta = 0.8
        elif load_filename:
            from topik.intermediaries.digested_document_collection import DigestedDocumentCollection
            self.corpus = DigestedDocumentCollection.load(load_filename)
            # total number of identified words for each given document (document length normalization factor?)
            self.each = map(sum, map(lambda x: x[1], self.corpus))
            # Maximum identified word (number of identified words in corpus)
            # TODO: seems like this could be tracked better during the tokenization step and fed in.
            self.words = max(reduce(operator.add, map(lambda x: x[0], self.corpus)))+1
            arrays = np.load(load_filename+".npz")
            self.zw = arrays['zw']
            self.dz = arrays['dz']
            self.dw_z = arrays['dw_z']
            self.p_dw = arrays['p_dw']
            self.beta, self.likelihood = arrays["beta_likelihood"]
        else:
            pass  # is just being used for inference

    def save(self, filename):
        np.savez_compressed(filename+".npz",
                            zw=self.zw,
                            dz=self.dz,
                            dw_z=self.dw_z,
                            p_dw=self.p_dw,
                            beta_likelihood=np.array([self.beta, self.likelihood]))
        saved_data = {"load_filename": filename}
        super(PLSA, self).save(filename, saved_data=saved_data)

    def _cal_p_dw(self):
        self.p_dw = []
        for d in xrange(self.docs):
            self.p_dw.append({})
            for w in self.corpus[d]:
                tmp = 0
                for _ in range(self.corpus[d][w]):
                    for z in xrange(self.topics):
                        tmp += (self.zw[z][w]*self.dz[d][z])**self.beta
                self.p_dw[-1][w] = tmp
        logging.debug('self.p_dw %r' % (self.p_dw,))

    def _e_step(self):
        self._cal_p_dw()
        self.dw_z = []
        for d in xrange(self.docs):
            self.dw_z.append({})
            for w in self.corpus[d]:
                self.dw_z[-1][w] = []
                for z in xrange(self.topics):
                    self.dw_z[-1][w].append(((self.zw[z][w]*self.dz[d][z])**self.beta)/self.p_dw[d][w])
        logging.debug('_e_step self.dw_z %r' % (self.dw_z,))

    def _m_step(self):
        for z in xrange(self.topics):
            self.zw[z] = [0]*self.words
            for d in xrange(self.docs):
                for w in self.corpus[d]:
                    self.zw[z][w] += self.corpus[d][w]*self.dw_z[d][w][z]
            norm = sum(self.zw[z])
            logging.debug('_m_step normalizers %r' % (norm,))
            for w in xrange(self.words):
                self.zw[z][w] /= norm
        for d in xrange(self.docs):
            self.dz[d] = [0]*self.topics
            for z in xrange(self.topics):
                for w in self.corpus[d]:
                    self.dz[d][z] += self.corpus[d][w]*self.dw_z[d][w][z]
            for z in xrange(self.topics):
                self.dz[d][z] /= self.each[d]
        logging.debug('_m_step zw %r dz %r' % (self.zw, self.dz))

    def _cal_likelihood(self):
        self.likelihood = 0
        for d in xrange(self.docs):
            for w in self.corpus[d]:
                self.likelihood += self.corpus[d][w]*math.log(self.p_dw[d][w])

    def train(self, max_iter=100):
        cur = 0
        for i in xrange(max_iter):
            print '%d iter' % i
            self._e_step()
            self._m_step()
            logging.debug('post _m_step zw %r dz %r' % (self.zw, self.dz))
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
            logging.debug('inference p_dw %r' % (p_dw))
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
        for topic in self.dz:
            word_ids = np.argpartition(topic, -topn)[-topn:]
            top_words.append([(topic[word_id], self.corpus.get_id2word_dict()[word_id]) for word_id in word_ids])
        return top_words

