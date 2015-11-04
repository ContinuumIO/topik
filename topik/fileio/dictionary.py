from ._registry import register_input, register_output
from .base_output import OutputInterface

@register_output
class InMemoryOutput(OutputInterface):
    def __init__(self, iterable=None, content_field=None, from_existing_corpus=False,
                 content_filter=None, models=None, vectorized_data=None, tokenized_data=None):
        super(InMemoryOutput, self).__init__()
        self.corpus = {}
        if from_existing_corpus:
            self.corpus = iterable
        elif iterable and content_field:
            self.import_from_iterable(iterable, content_field)
        else:
            raise ValueError("Output must be instantiated with iterable and ")
        self.content_filter = content_filter
        self.models = models if models else {}
        self.tokenized_data = tokenized_data if tokenized_data else {}
        self.vectorized_data = vectorized_data if vectorized_data else {}

    def get_generator_without_id(self, field=None):
        if not field:
            field = self.active_field
        for doc in self._documents.values():
            yield doc["_source"][field]

    def import_from_iterable(self, iterable, content_field):
        """
        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        """

        for item in iterable:
            if isinstance(item, basestring):
                item = {content_field: item}
            id = hash(item[content_field])
            self.corpus[id] = {"_source": item}

    # TODO: generalize for datetimes
    # TODO: validate input data to ensure that it has valid year data
    def get_date_filtered_data(self, start, end, filter_field="year"):
        return InMemoryOutput(content_field=self.content_field,
                                iterable=self._documents,
                                from_existing_corpus=True,
                                content_filter={"field": filter_field, "expression": "{}<=int({})<={}".format(start, "{}", end)})

    def save(self, filename):
        saved_data = {"iterable": self.corpus,
                      "from_existing_corpus": True,
                      "models": self.models,
                      "vectorized_data": self.vectorized_data,
                      "tokenized_data": self.tokenized_data,
                      "content_filter": self.content_filter}
        return super(InMemoryOutput, self).save(filename, saved_data)
