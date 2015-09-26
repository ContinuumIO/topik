[![Build Status](https://travis-ci.org/ContinuumIO/topik.svg?branch=master)](https://travis-ci.org/ContinuumIO/topik)
[![Coverage Status](https://coveralls.io/repos/ContinuumIO/topik/badge.svg?branch=master&service=github)](https://coveralls.io/github/ContinuumIO/topik?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ContinuumIO/topik/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ContinuumIO/topik/?branch=master)

# Topik

A Topic Modeling toolbox.


## Introduction

The aim of `topik` is to provide a full suite and high-level interface for anyone interested in applying topic modeling.
For that purpose, `topik` includes many utilities beyond statistical modeling algorithms and wraps all of its
features into an easy callable function and a command line interface.

`Topik` is built on top of existing topic modeling libraries and just provides a wrapper around them, for a quick and
easy exploratory analysis of your text data sets. The motivation of writing `topik` was and its starting point was
[gensim's](https://radimrehurek.com/gensim/) tutorials:

- [Gensim Streamed Corpora](http://radimrehurek.com/topic_modeling_tutorial/1%20-%20Streamed%20Corpora.html)
- [Gensim Topic Modeling](http://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html)


## Installation

```
conda install -c chdoig topik
```

## Use

```python
from topik.run import run_model

run_model(‘data.json', field='abstract', model='lda_online', r_ldavis=True, output_file=True)
```

## Results

- Output file:

Appends fields `tokens`, `lda_probabilities` and `topic_group`.

- tokens: extracted tokens from the document
- lda_probabilities: list of topic number and assigned lda probability
- topic_group: max lda probability topic

```json
{"tokens": ["deposited", "hfo", "surfaces", "chemical_vapor_deposition_cvd", "geh", "gehx", "deposited", "thermally", "cracking", "geh", "hot",
"tungsten", "filament", "oxidation", "bonding", "studied_ray_photoelectron_spectroscopy_xps", "geh", "geo", "geo", "desorption",
"measured_temperature_programmed_desorption", "tpd", "initially", "reacts", "dielectric", "forming", "oxide_layer", "followed", "deposition",
"formation", "nanocrystals", "cvd", "gehx", "deposited", "cracking", "rapidly", "forms", "contacting", "oxide_layer", "hfo", "stable", "fully", "removed",
"hfo", "surface", "annealing_results", "help", "explain", "stability", "nanocrystals", "contact", "hfo"],
"lda_probabilities": [[2, 0.048728168830183806], [3, 0.081054332141033983], [5, 0.10363835330016971], [7, 0.32014757577039443], [8, 0.35553044832357661], [9, 0.083351716411561097]],
"topic_group": 8}
```

- Visualization

Outputs [LDAvis](http://cpsievert.github.io/LDAvis/reviews/vis/#topic=7&lambda=0.6&term=) of your model to your browser.


## LICENSE

New BSD. See [License File](https://github.com/ContinuumIO/topik/blob/master/LICENSE.txt).

