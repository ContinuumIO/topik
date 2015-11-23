from __future__ import absolute_import

import gensim
from .base_model_output import ModelOutput
from ._registry import register
from .tests.test_data import test_vectorized_output

def _topic_term_to_array(id_term_map, topic):
    term_scores = {term: score for score, term in topic}
    return [term_scores[id_term_map[id]] for id in range(len(id_term_map))]

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
    >>> model = _LDA(test_vectorized_output, ntopics=3)

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
    unlabeled_doc_topic_matrix = list(_model[bow])
    doc_topic_matrix = {}
    doc_ids, _ = list(zip(*list(vectorized_output.get_vectors())))

    for i, doc in enumerate(unlabeled_doc_topic_matrix):
        doc_topic_matrix[doc_ids[i]] = []
        for topic in doc:
            doc_topic_matrix[doc_ids[i]].append(topic[1]) # topic[0] is the topic_id, topic[1] is the weight
    return topic_term_matrix, doc_topic_matrix


@register
def lda(vectorized_output, ntopics, **kwargs):
    return ModelOutput(vectorized_output, _LDA, ntopics=ntopics, **kwargs)
