import click

from topik.run import run_topic_model


@click.command(help='Run topic modeling')
@click.option("-d", "--data", required=True, help="Path to input data for topic modeling")
@click.option("-f", "--format", required=True, help="Data format provided: "
                 "json_stream, folder_files, large_json")
@click.option("-m", "--model", help="Statistical topic model: lda_batch, lda_online", default="./topic_model")
@click.option("-o", "--output", help="Topic modeling output path", default="./topic_model")
@click.option("-t", "--tokenizer", help="Tokenize method to use: "
                "simple, collocations, entities, mix", default='simple')
@click.option("-n", "--ntopics", help="Number of topics to find", default=10)
@click.option("--prefix_value", help="In 'large json' files, the prefix_value to extract text from", default=None)
@click.option("--event_value", help="In 'large json' files the event_value to extract text from", default=None)
@click.option("--field", help="In 'json stream' files, the field to extract text from", default=None)
def run(data, format, output, tokenizer, ntopics, prefix_value, event_value, field, model):
    run_topic_model(data=data, format=format, dir_path=output, tokenizer=tokenizer,n_topics=ntopics,
                       prefix_value=prefix_value, event_value=event_value, field=field, model=model)
