
# imports used only for doctests
from topik.tests import test_data_path


def collect_entities(collection, freq_min=2, freq_max=10000):
    """Return noun phrases from collection of documents.

    Parameters
    ----------
    collection: Corpus-base derived object or iterable collection of raw text
    freq_min: int
        Minimum frequency of a noun phrase occurrences in order to retrieve it. Default is 2.
    freq_max: int
        Maximum frequency of a noun phrase occurrences in order to retrieve it. Default is 10000.

    Examples
    --------
    >>> from topik.readers import read_input
    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
    >>> entities = collect_entities(raw_data)
    >>> len(entities)
    220
    """
    # TODO: add doctest

    from textblob import TextBlob

    np_counts_total = {}
    docs_examined = 0
    for doc in collection.get_generator_without_id():
        if docs_examined > 0 and docs_examined % 1000 == 0:
            sorted_phrases = sorted(np_counts_total.items(),
                                    key=lambda item: -item[1])
            np_counts_total = dict(sorted_phrases)
            logging.info("at document #%i, considering %i phrases: %s..." %
                         (docs_examined, len(np_counts_total), sorted_phrases[0]))

        for np in TextBlob(doc).noun_phrases:
            np_counts_total[np] = np_counts_total.get(np, 0) + 1
        docs_examined += 1

    # Remove noun phrases in the list that have higher frequencies than 'freq_max' or lower frequencies than 'freq_min'
    np_counts = {}
    for np, count in np_counts_total.items():
        if freq_max >= count >= freq_min:
            np_counts[np] = count

    return set(np_counts)

@register_tokenizer
def tokenize_entities(text, entities, min_length=1, stopwords=None):
    """A tokenizer that extracts noun phrases from text.

    Requires that you first establish entities using the collect_entities function

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords : None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> from topik.readers import read_input
    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), "abstract")
    >>> entities = collect_entities(raw_data)
    >>> tokenized_data = raw_data.tokenize(method="entities", entities=entities)
    >>> solution_tokens = [u'transition']
    >>> ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
    >>> solution_tokens in tokenized_texts
    True
    """

    from textblob import TextBlob
    result = []
    for np in TextBlob(text).noun_phrases:
        if np in entities:
            # filter out stop words
            tmp = "_".join(tokenize_simple(np, min_length=min_length, stopwords=stopwords))
            # if we end up with nothing, don't append an empty string
            if tmp:
                result.append(tmp)
    return result


@register_tokenizer
def tokenize_mixed(text, entities, min_length=1, stopwords=None):
    """A text tokenizer that retrieves entities ('noun phrases') first and simple words for the rest of the text.

    Parameters
    ----------
    text : str
        A single document's text to be tokenized
    entities : iterable of str
        Collection of noun phrases, obtained from collect_entities function
    min_length : int
        Minimum length of any single word
    stopwords: None or iterable of str
        Collection of words to ignore as tokens

    Examples
    --------
    >>> from topik.readers import read_input
    >>> raw_data = read_input('{}/test_data_json_stream.json'.format(test_data_path), content_field="abstract")
    >>> entities = collect_entities(raw_data)
    >>> tokenized_data = raw_data.tokenize(method="mixed", entities=entities,
    ...                                    min_length=3)
    >>> solution_tokens = [u'transition', u'metal', u'oxides', u'generation',
    ... u'materials', u'tantalum', u'oxide', u'nanometer', u'size', u'unusual',
    ... u'properties', u'sol', u'gel', u'method', u'dna', u'easy', u'method',
    ... u'biomedical', u'applications']
    >>> ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
    >>> solution_tokens in tokenized_texts
    True
    """

    from textblob import TextBlob
    result = []
    for np in TextBlob(text).noun_phrases:
        if ' ' in np and np not in entities:
            # break apart the noun phrase; it does not occur often enough in the collection of text to be considered.
            result.extend(tokenize_simple(np, min_length=min_length, stopwords=stopwords))
        else:
            # filter out stop words
            tmp = "_".join(tokenize_simple(np, min_length=min_length, stopwords=stopwords))
            # if we end up with nothing, don't append an empty string
            if tmp:
                result.append(tmp)
    return result