import cProfile
import pstats

from topik.run import run_model


# Create 5 set of stats
filenames = []
for i in range(1):
    filename = 'profile_stats_%d.stats' % i
    command_string = 	(	"run_model('topik/tests/data/autonomy-18-data_ry.json', "		+
    						"format='large_json', content_field='text', year_field="		+
    						"'datePublished', destination_es_instance='http://localhost:"	+
    						"9200', destination_es_index='topik', model='lda_online', "		+
    						"r_ldavis=True, output_file=True, clear_es_index=True, "		+
    						"prefix_value='item._source.isAuthorOf', event_value='string')")

    '''
    command_string = 	("run_model('topik/tests/data/test-data_json-stream.json', " 	+
    				 	"format='json_stream', content_field='abstract', year_field="	+
    				 	"'year', destination_es_instance='http://localhost:9200', "		+
    				 	"destination_es_index='topik', model='lda_online', r_ldavis="	+
    				 	"True, output_file=True, clear_es_index=True, start_year=2004, stop_year=2010)")
	'''
    cProfile.run('print %d, %s' % (i, command_string), filename)

# Read all 5 stats files into a single object
stats = pstats.Stats('profile_stats_0.stats')
#for i in range(1, 5):
#    stats.add('profile_stats_%d.stats' % i)

# Clean up filenames for the report
stats.strip_dirs()

# Sort the statistics by the cumulative time spent in the function
stats.sort_stats('cumulative')

stats.print_stats('__init__.py|cli.py|models.py|readers.py|run.py|tokenizers.py|utils.py|vectorizers.py|viz.py')