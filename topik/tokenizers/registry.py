


def tokenize(corpus, method="simple", synchronous_wait=30, **kwargs):
    """Convert data to lowercase; tokenize; create bag of words collection.

    Output from this function is used as input to modeling steps.

    raw_data: iterable corpus object containing the text to be processed.
        Each iteration call should return a new document's content.
    tokenizer_method: string id of tokenizer to use.  For keys, see
        topik.tokenizers.tokenizer_methods (which is a dictionary of classes)
    kwargs: arbitrary dicionary of extra parameters.  These are passed both
        to the tokenizer and to the vectorizer steps.
    """
    # create parameter string
    parameters_string = _get_parameters_string(method=method, **kwargs)
    token_path = "tokens_"+parameters_string

    # convert raw documents into lists of tokens
    for document_id, raw_document in corpus:
        tokenized_document = tokenizer_methods[method](raw_document,
                                     **kwargs)
        # TODO: would be nice to aggregate batches and append in bulk
        corpus.append_to_record(document_id, token_path, tokenized_document)
    corpus.synchronize(max_wait=synchronous_wait, field=token_path)

    # create a corpus dictionary
    id2word_dict = Dictionary(corpus.get_generator_without_id(
                                                        field=token_path))

    # use the corpus dictionary to generate BOWs from lists of tokens
    bow_path = "bow_"+parameters_string
    for document_id, tokenized_document in corpus.get_field(field=token_path):
        bow = {}
        for token_id, count in dict(id2word_dict.doc2bow(tokenized_document)).items():
            bow[token_id] = {'count': count}
        corpus.append_to_record(document_id, bow_path,
                              bow)

    return TokenizedCorpus(corpus.get_field(field=token_path),
                                      dictionary=id2word_dict)