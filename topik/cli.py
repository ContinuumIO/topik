import click

from topik.run import run_model


@click.command(help='Run topic modeling')
@click.option("-d", "--data", required=True, help="Path to input data for topic modeling")
@click.option("-c", "--field", help="the content field to extract text from, or for folders,"
              " the field to store text as", required=True)
@click.option("-f", "--format", default="auto", help="Data format provided: "
                 "json_stream, folder_files, large_json, solr, elastic")
@click.option("-m", "--model", help="Statistical topic model: lda, plsa", default="LDA")
@click.option("-o", "--output", help="Topic modeling output path", default="./topic_model")
@click.option("-t", "--tokenizer", help="Tokenize method to use: "
                "simple, collocations, entities, mix", default='simple')
@click.option("-n", "--ntopics", help="Number of topics to find", default=10)
@click.option("--termite", help="Whether to output a termite plot as a result", default=True)
@click.option("--ldavis", help="Whether to output an LDAvis-type plot as a result", default=False)
def run(data, format, output, tokenizer, ntopics, field, model, termite, ldavis):
    run_model(data_source=data, source_type=format, dir_path=output, tokenizer=tokenizer, n_topics=ntopics,
              content_field=field, model=model, r_ldavis=ldavis, termite_plot=termite)
