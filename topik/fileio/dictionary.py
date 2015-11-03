from ._registry import register_input, register_output
from .base_output import OutputInterface

@register_output
class InMemoryOutput(OutputInterface):
    def __init__(self, content_field, iterable=None, from_existing_corpus=False,
                 active_field=None, content_filter=None):
        super(InMemoryOutput, self).__init__()
        self.content_field = content_field
        if active_field is None:
            self.active_field = content_field
        else:
            self.active_field = active_field
        self._documents = {}
        if from_existing_corpus:
            self._documents = iterable
        elif iterable:
            self.import_from_iterable(iterable, content_field)

        self.idx = 0

        self.content_filter = content_filter

    @classmethod
    def class_key(cls):
        return "dictionary"

    def __iter__(self):
        for doc_id, doc in self._documents.items():
            if self.content_filter:
                if eval(self.content_filter["expression"].format(doc["_source"][self.content_filter["field"]])):
                    yield doc_id, doc["_source"][self.active_field]
            else:
                yield doc_id, doc["_source"][self.active_field]

    def __len__(self):
        return len(self._documents)

    @property
    def filter_string(self):
        return self.content_filter["expression"].format(self.content_filter["field"]) if self.content_filter else ""

    def append_to_record(self, record_id, field_name, field_value):
        if record_id in self._documents.keys():
            self._documents[record_id]["_source"][field_name] = field_value
        else:
            raise ValueError("No record with id '{}' was found.".format(record_id))

    def term_topic_matrix(self):
        self._term_topic_matrix={}

    def get_field(self, new_active_field=None):
        """Get a different field to iterate over, keeping all other details."""
        if not new_active_field:
            new_active_field = self.content_field
        return InMemoryOutput(active_field=new_active_field,
                                iterable=self._documents,
                                from_existing_corpus=True,
                                content_field=self.content_field)

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
            self._documents[id] = {"_source": item}

    # TODO: generalize for datetimes
    # TODO: validate input data to ensure that it has valid year data
    def get_date_filtered_data(self, start, end, filter_field="year"):
        return InMemoryOutput(content_field=self.content_field,
                                iterable=self._documents,
                                from_existing_corpus=True,
                                content_filter={"field": filter_field, "expression": "{}<=int({})<={}".format(start, "{}", end)})

    def save(self, filename, saved_data=None):
        if saved_data is None:
            saved_data = {"active_field": self.active_field, "content_field": self.content_field,
                          "iterable": self._documents,
                          "from_existing_corpus": True}
        return super(InMemoryOutput, self).save(filename, saved_data)
