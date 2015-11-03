

# imports used only for doctests
from topik.tests import test_data_path

@register_tokenizer
def tokenize_simple(text, min_length=1, stopwords=None):
    """A text tokenizer that simply lowercases, matches alphabetic
    characters and removes stopwords.

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
    >>> raw_data = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> tokenized_data = raw_data.tokenize()
    >>> ids, tokenized_texts = zip(*list(iter(tokenized_data._corpus)))
    >>> solution_tokens = [u'transition', u'metal', u'oxides', u'considered',
    ... u'generation', u'materials', u'field', u'electronics',
    ... u'advanced', u'catalysts', u'tantalum', u'v', u'oxide',
    ... u'reports', u'synthesis', u'material', u'nanometer', u'size',
    ... u'unusual', u'properties', u'work', u'present', u'synthesis',
    ... u'ta', u'o', u'nanorods', u'sol', u'gel', u'method', u'dna',
    ... u'structure', u'directing', u'agent', u'size', u'nanorods',
    ... u'order', u'nm', u'diameter', u'microns', u'length', u'easy',
    ... u'method', u'useful', u'preparation', u'nanomaterials', u'electronics',
    ... u'biomedical', u'applications', u'catalysts']
    >>> solution_tokens in tokenized_texts
    True
    """

    import gensim
    if not stopwords:
        from gensim.parsing.preprocessing import STOPWORDS as stopwords
    return [word for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords and len(word) >= min_length]
