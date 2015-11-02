

# imports used only for doctests
from topik.tests import test_data_path


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
    >>> from topik.fileio.readers import read_input
    >>> id_documents = read_input(
    ...                 '{}/test_data_json_stream.json'.format(test_data_path),
    ...                 content_field="abstract")
    >>> id, doc_text = next(iter(id_documents))
    >>> doc_text
    u'Transition metal oxides are being considered as the next generation \
materials in field such as electronics and advanced catalysts; between\
 them is Tantalum (V) Oxide; however, there are few reports for the \
synthesis of this material at the nanometer size which could have \
unusual properties. Hence, in this work we present the synthesis of \
Ta2O5 nanorods by sol gel method using DNA as structure directing \
agent, the size of the nanorods was of the order of 40 to 100 nm in \
diameter and several microns in length; this easy method can be useful\
 in the preparation of nanomaterials for electronics, biomedical \
applications as well as catalysts.'
    >>> tokens = tokenize_simple(doc_text)
    >>> tokens
    [u'transition', u'metal', u'oxides', u'considered', \
u'generation', u'materials', u'field', u'electronics', \
u'advanced', u'catalysts', u'tantalum', u'v', u'oxide', \
u'reports', u'synthesis', u'material', u'nanometer', u'size', \
u'unusual', u'properties', u'work', u'present', u'synthesis', \
u'ta', u'o', u'nanorods', u'sol', u'gel', u'method', u'dna', \
u'structure', u'directing', u'agent', u'size', u'nanorods', \
u'order', u'nm', u'diameter', u'microns', u'length', u'easy', \
u'method', u'useful', u'preparation', u'nanomaterials', u'electronics', \
u'biomedical', u'applications', u'catalysts']
    """

    import gensim
    if not stopwords:
        from gensim.parsing.preprocessing import STOPWORDS as stopwords
    return [word for word in gensim.utils.tokenize(text, lower=True)
            if word not in stopwords and len(word) >= min_length]
