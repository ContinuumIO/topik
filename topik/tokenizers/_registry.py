from functools import partial

from topik.singleton_registry import BaseRegistry, _base_register_decorator


class TokenizerRegistry(BaseRegistry):
    pass


# fill in the registration function
register = partial(_base_register_decorator, TokenizerRegistry)


# a nicer, more pythonic handle to our singleton instance
registered_tokenizers = TokenizerRegistry()


def tokenize(corpus, method="simple", **kwargs):
    """Break documents up into component words, optionally eliminating stopwords.

    Output from this function is used as input to vectorization steps.

    raw_data: iterable corpus object containing the text to be processed.
        Each iteration call should return a new document's content.
    method: string id of tokenizer to use.  For keys, see
        topik.tokenizers.registered_tokenizers (which is a dictionary of functions)
    kwargs: arbitrary dicionary of extra parameters.
    """
    return TokenizerRegistry()[method](corpus, **kwargs)
