from ._registry import register

@register
def tfidf(tokenized_input):
    raise NotImplementedError