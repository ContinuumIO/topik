"""
This file is concerned with preparing input to modeling.

Put things like lowercasing, tokenizing, and vectorizing here.

Generally, methods to process text operate on single documents at a time.  This
is done to facilitate parallelization over collections.
"""

import itertools

import gensim

# this is our output from whatever preprocessing we do.  It is input to modeling step.
from topik.intermediaries.digested_document_collection import DigestedDocumentCollection
from topik.tokenizers import tokenizer_methods
from topik.utils import _iter_corpus


def _get_parameter_string(**kwargs):
    """Used to create identifiers for output"""
    id = ''.join('{}={},'.format(key, val) for key, val in sorted(kwargs.items()))
    return id[:-1]


def _to_lower(raw_record):
    return raw_record.lower()


def _tokenize(raw_record, method="simple", **tokenizer_kwargs):
    """Tokenize a single document into individual words"""
    tokenized_document = tokenizer_methods[method](raw_record, **tokenizer_kwargs)
    return tokenized_document


def _to_bag_of_words(data_object, **kwargs):
    tokenized_docs = data_object.get_generator_without_id("tokens_"+_get_parameter_string(**kwargs))
    return gensim.corpora.Dictionary(tokenized_docs)


def preprocess(raw_data, tokenizer_method="simple", **kwargs):
    """Convert data to lowercase; tokenize; create bag of words collection.

    Output from this function is used as input to modeling steps.

    raw_data: iterable corpus object containing the text to be processed.
        Each iteration call should return a new document's content.
    tokenizer_method: string id of tokenizer to use.  For keys, see
        topik.tokenizers.tokenizer_methods (which is a dictionary of classes)
    kwargs: arbitrary dicionary of extra parameters.  These are passed both
        to the tokenizer and to the vectorizer steps.
    """
    parameters_string = _get_parameter_string(**kwargs)
    token_path = "tokens_"+parameters_string
    for record_id, raw_record in raw_data:
        tokenized_record = _tokenize(_to_lower(raw_record),
                                     method=tokenizer_method,
                                     **kwargs)
        # TODO: would be nice to aggregate batches and append in bulk
        raw_data.append_to_record(record_id, token_path, tokenized_record)
    word_dict = _to_bag_of_words(raw_data, **kwargs)
    return DigestedDocumentCollection(raw_data.get_field(field=token_path), word_dict)
