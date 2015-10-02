Output formats
^^^^^^^^^^^^^^

Outputs from read_input are always a subclass of the topik.intermediaries.raw_data.CorpusInterface class.  This abstract class defines an interface and encourages standardized behavior, ensuring interchangeability of many storage backends.  This interface provides the following features:

  * The object is iterable.  Iterating over it returns a document ID and the document text specified by "content_field"
  * The object has a class_key method that returns a string to store the class as in topik.registered_outputs
  * The object implements __len__, so that people can call len(object)
  * The object has a get_generator_without_id method to get a generator yeilding only document text.  This is useful when feeding data to external tools, but loses the ability to tie results to specific documents.  A field may be specified to yield something other than the content_field initially provided at import time.
  * The object has a filter_string property, returning a string representing the filter to access the current subset of the complete corpus.
  * The object implements a get_date_filtered_data method to filter results according to date record.  Start, end, and field to use must be specified in any method call.
  * The object implements an append_to_record method that appends data to the document record.  This is used to store tokenization results and some model intermediates.
  * The object can, but is not required to implement a save method, describing what metadata is necessary to recreate the object.  Present implementations override this function to provide defaults for the saved metadata.  If you override this method, be sure to call the superclass method, or implement all of its functionality.


Additional formats can be registered using the topik.intermediares.raw_data.register_output function.

It is best to implement the CorpusInterface class by subclassing it.  It is not strictly required, but if your class does not subclass it and does not follow its interface, then the rest of Topik is unlikely to work with your class.  You are certainly free to implement additional methods and members, but the interface ensures a minimum level of functionality expected by the rest of the system.
