from topik.tokenizers.ngrams import _collect_bigrams_and_trigrams, \
    _collocation_document, ngrams

sample_data = [("doc1", str(u"Frank the Stank-Tank walked his sassy unicorn, Brony,"
                            u" to prancercise class daily.  Prancercise was "
                            u"a tremendously popular pastime of sassy "
                            u"unicorns and retirees alike.")),
                ("doc2", str(u"Prancercise is a form of both art and fitniss, "
                         u"originally invented by sassy unicorns. It has "
                         u"recently been popularized by such retired "
                         u"celebrities as Frank The Stank-Tank.")),
                ]


x = ngrams(sample_data, freq_bounds=[(2,100),(2,100)])
#print(list(x))

def test__collect_bigrams_and_trigrams():
    bigrams_and_trigrams = _collect_bigrams_and_trigrams(sample_data, min_freqs=[2,2])
    assert(bigrams_and_trigrams[0].pattern == u'(frank stank|stank tank|sassy unicorns)')
    assert(bigrams_and_trigrams[1].pattern == u'(frank stank tank)')


def test__collocation_document():
    bigrams_and_trigrams = _collect_bigrams_and_trigrams(sample_data, min_freqs=[2,2])
    assert(_collocation_document(sample_data[0][1],bigrams_and_trigrams) == [
        u'frank_stank', u'tank', u'walked', u'sassy', u'unicorn', u'brony',
         u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
         u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike'
    ])

    assert(_collocation_document(sample_data[1][1],bigrams_and_trigrams) == [
        u'prancercise', u'form', u'art', u'fitniss', u'originally',
         u'invented', u'sassy_unicorns', u'recently', u'popularized',
         u'retired', u'celebrities', u'frank_stank', u'tank'
    ])

def test_ngrams():
    tokenized_data = ngrams(sample_data, freq_bounds=[(2,100),(2,100)])
    assert(next(tokenized_data) == [
        ('doc1', [
            u'frank_stank', u'tank', u'walked', u'sassy', u'unicorn', u'brony',
            u'prancercise', u'class', u'daily', u'prancercise', u'tremendously',
            u'popular', u'pastime', u'sassy_unicorns', u'retirees', u'alike'
                 ]),
        ('doc2', [
            u'prancercise', u'form', u'art', u'fitniss', u'originally',
            u'invented', u'sassy_unicorns', u'recently', u'popularized',
            u'retired', u'celebrities', u'frank_stank', u'tank'
            ])
    ])