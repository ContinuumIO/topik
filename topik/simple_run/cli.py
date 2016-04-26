import click
import logging
import sys
from topik.simple_run.run import run_pipeline

logging.basicConfig(stream=sys.stdout, format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

@click.command(help='Run topic modeling')
@click.option("-d", "--data", required=True, help="Path to input data for topic modeling")
@click.option("-c", "--field", help="the content field to extract text from, or for folders,"
              " the field to store text as", required=True)
@click.option("-f", "--format", default="auto", help="Data format provided: "
                 "json_stream, folder_files, large_json, solr, elastic")
@click.option("-m", "--model", help="Statistical topic model: lda, plsa", default="lda")
@click.option("-o", "--output", help="Topic modeling output path", default="./topic_model")
@click.option("-t", "--tokenizer", help="Tokenize method to use: "
                "simple, entities, mixed, ngrams", default='simple')
@click.option("-v", "--vectorizer", help="Vectorize method to use: "
                "bag_of_words, tfidf.  Note: tfidf not compatible with lda models",
              default="bag_of_words")
@click.option("-n", "--ntopics", help="Number of topics to find", default=10)
@click.option("--termite", help="Whether to output a termite plot as a result", default=False)
@click.option("--lda_vis", help="Whether to output an LDAvis-type plot as a result", default=True)
def run(data, format, output, tokenizer, vectorizer, ntopics, field, model,
        termite, lda_vis):
    run_pipeline(data_source=data, source_type=format, dir_path=output,
                 tokenizer=tokenizer, vectorizer=vectorizer, ntopics=ntopics,
                 content_field=field, model=model, lda_vis=lda_vis,
                 termite_plot=termite)
