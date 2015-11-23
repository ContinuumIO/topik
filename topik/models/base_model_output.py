class ModelOutput(object):
    """Abstract base class for topic models.

    Ensures consistent interface across models, for base result display capabilities.

    Attributes
    ----------
    _doc_topic_matrix : mapping of document ids to weights for topic indices
                        matrix storing the relative topic weights for each document
    _topic_term_matrix : mapping of terms to each topic
    """
    def __init__(self, vectorized_corpus=None, model_func=None,
                 vocab=None, term_frequency=None, topic_term_matrix=None,
                 doc_lengths=None, doc_topic_matrix=None, **kwargs):
        if vectorized_corpus and model_func:
            self._vocab = vectorized_corpus.id_term_map
            self._doc_lengths = vectorized_corpus.doc_lengths
            self._term_frequency = vectorized_corpus.term_frequency
            self._topic_term_matrix, self._doc_topic_matrix = model_func(
                                                    vectorized_corpus, **kwargs)

        elif (vocab and term_frequency and topic_term_matrix and doc_lengths and
                     doc_topic_matrix):
            self._vocab = vocab
            self._term_frequency = term_frequency
            self._topic_term_matrix = topic_term_matrix
            self._doc_lengths = doc_lengths
            self._doc_topic_matrix = doc_topic_matrix
        else:
            raise ValueError("Must provide either vectorized corpus and model func, "
                             "or term data and doc data.")

    @property
    def vocab(self):
        return self._vocab

    @property
    def term_frequency(self):
        return self._term_frequency

    @property
    def topic_term_matrix(self):
        return self._topic_term_matrix

    @property
    def doc_lengths(self):
        return self._doc_lengths

    @property
    def doc_topic_matrix(self):
        return self._doc_topic_matrix


