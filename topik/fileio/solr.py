import pysolr

from ._registry import register_input


@register_input
def solr(solr_instance, content_field, query="*:*", content_in_list=True, **kwargs):
    # TODO: should I be checking for presence of content_field and year_field?
    # If not then we don't need them as params
    # TODO: should I care at this level whether the content_in_list or only at
    # the read_input level?  Is it being handled at that level currently?
    """Iterate over all documents in the specified solr intance that match the specified query

    Parameters
    ----------
    solr_instance : str
        Address of the solr instance
    content_field : str
        The name fo the field that contains the main text body of the document.
    query : str
        The solr query string
    content_in_list: bool
        Whether the source fields are stored in single-element lists.  Used for unpacking.
    """

    s = pysolr.Solr(solr_instance)
    results_per_batch = 100
    response = s.select(query, rows=results_per_batch)
    while response.results:
        for item in response.results:
            if content_in_list:
                if content_field in item.keys() and type(item[content_field]) == list:
                    item[content_field] = item[content_field][0]
            yield item
        response = response.next_batch()

