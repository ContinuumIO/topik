from topik.tokenizers.entities import _collect_entities, \
    _tokenize_entities_document, _tokenize_mixed_document, \
    entities, mixed

sample_data = [
        ("doc1", str(u"Frank the Swank-Tank walked his sassy unicorn, Brony,"
                    u" to prancercise class daily.  Prancercise was "
                    u"a tremendously popular pastime of sassy "
                    u"unicorns and retirees alike.")),
        ("doc2", str(u"Prancercise is a form of both art and fitniss, "
                    u"originally invented by sassy unicorns. It has "
                    u"recently been popularized by such retired "
                    u"celebrities as Frank The Swank-Tank."))]

ents = _collect_entities(sample_data)

def test__collect_entities():
    assert(ents == {'frank', 'swank-tank', 'prancercise', u'sassy unicorns'})

def test__tokenize_entities_document():
    tokenized_doc1 = _tokenize_entities_document(sample_data[0][1], ents)
    assert(tokenized_doc1 == [u'frank', u'swank_tank', u'prancercise',
                              u'sassy_unicorns'])
    tokenized_doc2 = _tokenize_entities_document(sample_data[1][1], ents)
    assert(tokenized_doc2 == [u'prancercise', u'sassy_unicorns', u'frank',
                              u'swank_tank'])

def test_tokenize_mixed_document():
    tokenized_doc1 = _tokenize_mixed_document(sample_data[0][1], ents)
    assert(tokenized_doc1 == [
        u'frank', u'swank_tank', u'sassy', u'unicorn', u'brony', u'prancercise',
        u'class', u'prancercise', u'popular', u'pastime', u'sassy_unicorns'])
    tokenized_doc2 = _tokenize_mixed_document(sample_data[1][1], ents)
    assert(tokenized_doc2 == [
        u'prancercise', u'sassy_unicorns', u'frank', u'swank_tank'])

def test_entities():
    tokenized_corpora = entities(sample_data)
    assert(next(tokenized_corpora) == \
        ('doc1', [u'frank', u'swank_tank', u'prancercise', u'sassy_unicorns']))
    assert(next(tokenized_corpora) == \
        ('doc2', [u'prancercise', u'sassy_unicorns', u'frank', u'swank_tank']))

def test_mixed():
    tokenized_corpora = mixed(sample_data)
    assert(next(tokenized_corpora) == \
           ('doc1', [u'frank', u'swank_tank', u'sassy', u'unicorn', u'brony',
                     u'prancercise', u'class', u'prancercise', u'popular',
                     u'pastime', u'sassy_unicorns']))
    assert(next(tokenized_corpora) == \
           ('doc2', [u'prancercise', u'sassy_unicorns', u'frank',
                     u'swank_tank']))
