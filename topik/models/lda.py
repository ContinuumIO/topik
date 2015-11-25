from __future__ import absolute_import, print_function

import gensim
import numpy

from .base_model_output import ModelOutput
from ._registry import register
from .tests.test_data import test_vectorized_output


def _topic_term_to_array(id_term_map, topic):
    term_scores = {term: float(score) for score, term in topic}
    return [term_scores[id_term_map[id]] for id in range(len(id_term_map))]


def _doc_topic_to_array(vectors_for_ids, doc_topic_output):
    ids = [id for id in vectors_for_ids]
    collapsed_output = [[float(weight) for topic, weight in doc] for doc in doc_topic_output]
    return {id: vector for id, vector in zip(ids, collapsed_output)}


def _LDA(vectorized_output, ntopics, **kwargs):
    """A high-level interface for an LDA (Latent Dirichlet Allocation) model.


    Parameters
    ----------
    corpus_input : CorpusBase-derived object
        object fulfilling basic Corpus interface (preprocessed, tokenized text).
        see topik.fileio.tokenized_corpus for more info.
    ntopics : int
        Number of topics to model
    load_filename : None or str
        If not None, this (JSON) file is read to determine parameters of the model persisted to disk.
    binary_filename : None or str
        If not None, this file is loaded by Gensim to bring a disk-persisted model back into memory.


    Attributes
    ----------
    corpus : CorpusBase-derived object, tokenized
    model : Gensim LdaModel instance


    Examples
    --------
    >>> numpy.random.seed(42)
    >>> topic_term_matrix, doc_topic_matrix = _LDA(test_vectorized_output, ntopics=3)
    >>> print(doc_topic_matrix)
    {'doc2': [0.807951743410802, 0.10476330970525315, 0.08728494688394486], \
'doc1': [0.062042881984474524, 0.8802767497765115, 0.057680368239013936]}
    >>> print(topic_term_matrix)
    {'topic1': [0.06013569863803469, 0.5215928367150972, 0.2121197471377498, 0.2061517175091185], \
'topic0': [0.29823981660082644, 0.31304629647623466, 0.3050111012538884, 0.08370278566905044], \
'topic2': [0.2433294456376143, 0.26854719743019123, 0.25425967705367086, 0.23386367987852355]}
    """
    # the minimum_probability=0 argument is necessary in order for
    # gensim to return the full document-topic-distribution matrix.  If
    # this argument is omitted and left to the gensim default of 0.01,
    # then all document-topic weights below that threshold will be
    # returned as NaN, violating the subsequent LDAvis assumption that
    # all rows (documents) in the document-topic-distribution matrix sum
    # to 1.

    bow = [[(k, v) for k, v in vector.items()] for vector in vectorized_output.vectors.values()]
    _model = gensim.models.LdaModel(bow,
                                    num_topics=ntopics,
                                    id2word=vectorized_output.id_term_map,
                                    minimum_probability=0, **kwargs)
    topic_term_matrix = {"topic{}".format(topic_no): _topic_term_to_array(vectorized_output.id_term_map,
                                                                          _model.show_topic(topic_no, None))
                         for topic_no in range(ntopics)}
    doc_topic_matrix = list(_model[bow])

    doc_topic_matrix = _doc_topic_to_array(vectorized_output.vectors, doc_topic_matrix)

    return topic_term_matrix, doc_topic_matrix


@register
def lda(vectorized_output, ntopics, **kwargs):
    return ModelOutput(vectorized_corpus=vectorized_output, model_func=_LDA, ntopics=ntopics, **kwargs)
