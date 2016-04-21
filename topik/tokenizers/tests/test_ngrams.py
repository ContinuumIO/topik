from topik.tokenizers.ngrams import _collect_ngrams, \
    _collocation_document, ngrams
from nose.tools import nottest
sample_data = [
        ("doc1", str(u"Frank the Swank-Tank walked his sassy unicorn, Brony,"
                     u" to prancercise class daily.  Prancercise was "
                     u"a tremendously popular pastime of sassy "
                     u"unicorns and retirees alike.")),
        ("doc2", str(u"Frank the Swank-Tank was also known as Big Daddy Workout Queen "
                     u"as he loved to cross-dress while prancercising."
                     u"Dressing up as a sassy unicorn to match Brony was a key "
                     u"source of enjoyment for both him and the onlooking retirees.")),
        ("doc3", str(u"Big Daddy Workout Queen knew that the best way to get "
                     u"more people to embrace prancercise was to "
                     u"wear flashy outfits with tassels and bells.")),
        ("doc3", str(u"Prancercise is a form of both art and fitness, "
                     u"originally invented by sassy unicorns. It has "
                     u"recently been popularized by such retired "
                     u"celebrities as Frank The Swank-Tank (aka Big Daddy Workout Queen)"))]


@nottest
def generator():
    for item in sample_data:
        yield item


def test__collect_ngrams():
    result_ngrams = _collect_ngrams(sample_data, min_freqs=[2, 2, 2])
    assert(result_ngrams[0].pattern ==
           u'(big daddy|daddy workout|frank swank|swank tank|workout queen|sassy unicorn|sassy unicorns)')
    assert(result_ngrams[1].pattern == u'(big daddy workout|daddy workout queen|frank swank tank)')
    assert(result_ngrams[2].pattern == u'(big daddy workout queen)')


def test__collocation_document():
    these_ngrams = _collect_ngrams(sample_data, min_freqs=[2, 2, 2])
    assert(_collocation_document(sample_data[0][1],these_ngrams) == [
        u'frank_swank', u'tank', u'walked', u'sassy_unicorn', u'brony',
        u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
        u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike'
    ])

    assert(_collocation_document(sample_data[1][1],these_ngrams) == [
        u'frank_swank', u'tank', u'known', u'big_daddy', u'workout_queen',
        u'loved', u'cross', u'dress', u'prancercising', u'dressing',
        u'sassy_unicorn', u'match', u'brony', u'key', u'source', u'enjoyment',
        u'onlooking', u'retirees'])


def test_ngrams_list():
    freq_bounds = [(2, 100), (2, 100), (2, 100)]
    tokenized_corpora = ngrams(sample_data, freq_bounds=freq_bounds)
    assert(len(freq_bounds) == 3)
    assert(next(tokenized_corpora) == (
        'doc1', [
            u'frank_swank', u'tank', u'walked', u'sassy_unicorn', u'brony',
            u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
            u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike'
                 ]))
    assert(next(tokenized_corpora) == (
        'doc2', [
            u'frank_swank', u'tank', u'known', u'big_daddy', u'workout_queen',
            u'loved', u'cross', u'dress', u'prancercising',
            u'dressing', u'sassy_unicorn', u'match', u'brony', u'key', u'source',
            u'enjoyment', u'onlooking', u'retirees']))


def test_ngrams_generator():
    freq_bounds = [(2, 100), (2, 100), (2, 100)]
    corpus_gen = generator()
    tokenized_corpora = ngrams(corpus_gen, freq_bounds=freq_bounds)
    assert(len(freq_bounds) == 3)
    assert(next(tokenized_corpora) == (
        'doc1', [
            u'frank_swank', u'tank', u'walked', u'sassy_unicorn', u'brony',
            u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
            u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike'
                 ]))
    assert(next(tokenized_corpora) == (
        'doc2', [
            u'frank_swank', u'tank', u'known', u'big_daddy', u'workout_queen',
            u'loved', u'cross', u'dress', u'prancercising',
            u'dressing', u'sassy_unicorn', u'match', u'brony', u'key', u'source',
            u'enjoyment', u'onlooking', u'retirees']))