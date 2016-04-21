#!/usr/bin/env python

from __future__ import absolute_import, print_function


from stop_words import get_stop_words
import numpy as np
import logging
import sys

from string import ascii_letters
from topik.fileio import read_input
from topik import tokenizers, vectorizers, models, visualizers
from topik.visualizers.termite_plot import termite_html
from topik.ish_inspector import ipsh

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# config
data_source="/data/hep_articles_2"
source_type = "auto"
content_field = "text"
tokenizer = "entities"
seed=42
model = 'lda'
vectorizer = 'tfidf'
ntopics=20
min_length=3
stopwords = get_stop_words("en")

np.random.seed(seed)
logger.info("Loading data as {} from {}".format(source_type, data_source))
raw_data = read_input(data_source, content_field=content_field,
                      source_type=source_type)
# disable HASHing
#raw_data = ((hash(item[content_field]), item[content_field]) for item in raw_data)
raw_data = ((item['filename'], item[content_field]) for item in raw_data)
logger.info("Tokenizing data with {}".format(tokenizer))
tokenized_data = tokenizers.registered_tokenizers[tokenizer](raw_data, min_length=min_length, stopwords=stopwords)
logger.info("Vectorizing data with {} min_length: {}".format(vectorizer, min_length))
vectorized_data = vectorizers.registered_vectorizers[vectorizer](tokenized_data)
logger.info("Running {} model for {} topics".format(model,ntopics))
model = models.registered_models[model](vectorized_data, ntopics=ntopics)
#if not os.path.exists(dir_path):
#    os.mkdir(dir_path)
#termite_html(model, filename="/var/www/html/termite.html", plot_title="Termite plot", topn=15)

visualizers.visualize(model, "save_html", filename ='/var/www/html/ldavis.html')
