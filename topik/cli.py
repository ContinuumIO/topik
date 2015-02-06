from __future__ import absolute_import

import os

from topik.readers import iter_document_json_stream, iter_documents_folder
from topik.tokenizers import (SimpleTokenizer, CollocationsTokenizer,
                                EntitiesTokenizer, MixedTokenizer)

from topik.vectorizers import CorpusBOW
from topik.models import LDA
from topik.viz import Termite


import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="TOPIC SPACE")

    parser.add_argument("-d", "--data", required=True, action = "store", help="Path to input data for topic modeling ")
    parser.add_argument("-f", "--format", action = "store", help="Data format provided: "
                                                                 "Currently available:"
                                                                 "streaming_json, folder_files", default='streaming_json')
    parser.add_argument("-n", "--name", action="store", help="Topic modeling name", default="topic_model")
    parser.add_argument("-p", "--preprocessing", action = "store",
                        help="Tokenize method to use id: "
                             "1-Simple, 2-Collocations, 3-Entities, 4-Mix", defaul='1')
    parser.add_argument("-t", "--topics", action = "store",
                       help="Number of topics to find", default='10')

    return parser.parse_args()


def main():
    args = parse_args()
    ntopics = int(args.topics)

    if args.data:
        # Select reader depending on `--format` argument given.
        if args.format == 'folder_files':
            documents = iter_documents_folder(args.data)
        else:
            documents = iter_document_json_stream(args.data)

        if args.preprocessing == "1":
            corpus = SimpleTokenizer(documents)
        elif args.preprocessing == "2" :
            corpus = CollocationsTokenizer(documents)
        elif args.preprocessing == "3":
            corpus = EntitiesTokenizer(documents)
        elif args.preprocessing == "4":
            corpus = MixedTokenizer(documents)
        else:
            print("Processing value invalid, using 1-Simple by default")
            corpus = SimpleTokenizer(documents)
        name = args.name
        os.makedirs(name)
        path = name
        # Create dictionary
        corpus_bow = CorpusBOW(corpus)
        corpus_dict = corpus_bow.save_dict(os.path.join(path,'%s.dict' % name))
        # Serialize and store the corpus
        corpus_bow.serialize(os.path.join(path,'%s.mm' % name))
        # Create LDA model from corpus and dictionary
        lda = LDA(os.path.join(path,'%s.mm' % name), os.path.join(path,'%s.dict' % name), ntopics)
        # Generate the input for the termite plot
        lda.termite_data(os.path.join(path,'%s_termite.csv' % name))
        # Get termite plot for this model
        termite = Termite(os.path.join(path,'%s_termite.csv' % name), "Termite Plot for %s" % name)
        termite.plot(os.path.join(path,'%s_termite.html' %name))

        #get_documents_output_file(args.data, corpus_bow, corpus_dict, lda.model, name)

if __name__ == "__main__":

    main()