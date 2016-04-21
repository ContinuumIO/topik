from ._registry import register_input


@register_input
def read_elastic(hosts, **kwargs):
    """Iterate over all documents in the specified elasticsearch intance and index that match the specified query.

    kwargs are passed to Elasticsearch class instantiation, and can be used to pass any additional options
    described at https://elasticsearch-py.readthedocs.org/en/master/

    Parameters
    ----------
    hosts : str or list
        Address of the elasticsearch instance any index.  May include port, username and password.
        See https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch for all options.

    content_field : str
        The name fo the field that contains the main text body of the document.

    **kwargs: additional keyword arguments to be passed to Elasticsearch client instance and to scan query.
              See
              https://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch for all client options.
              https://elasticsearch-py.readthedocs.org/en/master/helpers.html#elasticsearch.helpers.scan for all scan options.
    """
    # TODO: add doctest
    from elasticsearch import Elasticsearch, helpers
    es = Elasticsearch(hosts, **kwargs)
    results = helpers.scan(es, **kwargs)
    for result in results:
        yield result['_source']



