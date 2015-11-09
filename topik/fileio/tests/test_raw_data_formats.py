import unittest
import os
import time

import elasticsearch
from topik.fileio import read_input
from topik.fileio.base_output import load_persisted_corpus, ElasticSearchCorpus
from topik.fileio.tests import test_data_path

INDEX = "topik_unittest"
SAVE_FILENAME = "test_save"


