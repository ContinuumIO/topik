from abc import ABCMeta, abstractmethod
import logging

import pandas as pd
from six import with_metaclass

# doctest-only imports
from topik.preprocessing import preprocess
from topik.readers import read_input
from topik.tests import test_data_path


class TopicModelBase(with_metaclass(ABCMeta)):

    @abstractmethod
    def get_top_words(self, topn):
        pass

    def termite_data(self, filename="termite.csv", topn_words=15):
        """Generate the csv file input for the termite plot.

        Parameters
        ----------
        filename: string
            Desired name for the generated csv file

        >>> raw_data = read_input(
            '{}/test-data-1.json', "text")
        >>> processed_data = preprocess(raw_data)  # preprocess returns a DigestedDocumentCollection
        >>> model = LDA(processed_data, ntopics=3)
        >>> model.termite_data('termite.csv', 15)
        
        """.format(test_data_path)
        count = 1
        for topic in self.get_top_words(topn_words):
            if count == 1:
                df_temp = pd.DataFrame(topic, columns=['weight', 'word'])
                df_temp['topic'] = pd.Series(count, index=df_temp.index)
                df = df_temp
            else:
                df_temp = pd.DataFrame(topic, columns=['weight', 'word'])
                df_temp['topic'] = pd.Series(count, index=df_temp.index)
                df = df.append(df_temp, ignore_index=True)
            count += 1
        logging.info("saving termite plot input csv file to %s " % filename)
        df.to_csv(filename, index=False, encoding='utf-8')
        return df
