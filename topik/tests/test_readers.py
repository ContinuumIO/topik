import unittest

import nose.tools as nt
import elasticsearch

from topik.readers import read_input
import topik.readers as readers
from topik.intermediaries.raw_data import ElasticSearchCorpus
from topik.tests import test_data_path

INDEX = "test_elastic"

class TestReader(unittest.TestCase):

    def setUp(self):
        self.solution_1 = str("'Interstellar' was incredible. The visuals, the score, the acting, were all amazing."
                              " The plot is definitely one of the most original I've seen in a while.")
        self.solution_2 = str('In this paper, we describe a simple and rapid solution-phase chemical reduction method'
                              ' with no inert gas protection, for preparing stable copper nanoparticle colloid with'
                              ' average particle size of 3.4 nm and narrow size distribution. In our synthesis route,'
                              ' ascorbic acid, natural vitamin C (VC), serves as both a reducing agent and an'
                              ' antioxidant to reduce copper salt precursor and effectively prevent the general'
                              ' oxidation process occurring to the newborn nanoparticles. XRD and UV/vis confirm the'
                              ' formation of pure face-centered cubic (fcc) copper nanoparticles and the excellent'
                              ' antioxidant ability of ascorbic acid.')
        self.solution_3 =   "Potential-function-based control strategy for path planning and formation control of Quadrotors is proposed in this work. The potential function is used to attract the Quadrotor to the goal location as well as avoiding the obstacle. The algorithm to solve the so called local minima problem by utilizing the wall-following behavior is also explained. The resulted path planning via potential function strategy is then used to design formation control algorithm. Using the hybrid virtual leader and behavioral approach schema, the formation control strategy by means of potential function is proposed. The overall strategy has been successfully applied to the Quadrotor's model of Parrot AR Drone 2.0 in Gazebo simulator programmed using Robot Operating System.\nAuthor(s) Rizqi, A.A.A. Dept. of Electr. Eng. & Inf. Technol., Univ. Gadjah Mada, Yogyakarta, Indonesia Cahyadi, A.I. ; Adji, T.B.\nReferenced Items are not available for this document.\nNo versions found for this document.\nStandards Dictionary Terms are available to subscribers only."
        '''(u"Potential-function-based control strategy for path planning and formation control of" +
                            u"Quadrotors is proposed in this work. The potential function is used to attract the " +
                            u"Quadrotor to the goal location as well as avoiding the obstacle. The algorithm to " +
                            u"solve the so called local minima problem by utilizing the wall-following behavior " +
                            u"is also explained. The resulted path planning via potential function strategy is " +
                            u"then used to design formation control algorithm. Using the hybrid virtual leader and " +
                            u"behavioral approach schema, the formation control strategy by means of potential " +
                            u"function is proposed. The overall strategy has been successfully applied to the " +
                            u"Quadrotor's model of Parrot AR Drone 2.0 in Gazebo simulator programmed using Robot " +
                            u"Operating System.\nAuthor(s) Rizqi, A.A.A. Dept. of Electr. Eng. & Inf. Technol., " +
                            u"Univ. Gadjah Mada, Yogyakarta, Indonesia Cahyadi, A.I. ; Adji, T.B.\nReferenced Items " +
                            u"are not available for this document.\nNo versions found for this document.\nStandards " +
                            u"Dictionary Terms are available to subscribers only.")'''
        #self.solution_4 = 'Transition metal oxides are being considered as the next generation materials in field such as electronics and advanced catalysts; between them is Tantalum (V) Oxide; however, there are few reports for the synthesis of this material at the nanometer size which could have unusual properties. Hence, in this work we present the synthesis of Ta2O5 nanorods by sol gel method using DNA as structure directing agent, the size of the nanorods was of the order of 40 to 100 nm in diameter and several microns in length; this easy method can be useful in the preparation of nanomaterials for electronics, biomedical applications as well as catalysts.'
        self.solution_4 = str("Transition metal oxides are being considered as the next generation materials in field "
                              "such as electronics and advanced catalysts; between them is Tantalum (V) Oxide; however"
                              ", there are few reports for the synthesis of this material at the nanometer size which "
                              "could have unusual properties. Hence, in this work we present the synthesis of Ta2O5 "
                              "nanorods by sol gel method using DNA as structure directing agent, the size of the "
                              "nanorods was of the order of 40 to 100 nm in diameter and several microns in length; "
                              "this easy method can be useful in the preparation of nanomaterials for electronics, "
                              "biomedical applications as well as catalysts.")
        '''str(  u"Transition metal oxides are being considered as the next generation materials in field"
                                u"such as electronics and advanced catalysts; between them is Tantalum (V) Oxide; "
                                u"however, there are few reports for the synthesis of this material at the nanometer "
                                u"size which could have unusual properties. Hence, in this work we present the "
                                u"synthesis of Ta2O5 nanorods by sol gel method using DNA as structure directing agent, "
                                u"the size of the nanorods was of the order of 40 to 100 nm in diameter and several "
                                u"microns in length; this easy method can be useful in the preparation of nanomaterials "
                                u"for electronics, biomedical applications as well as catalysts.")'''

    def tearDown(self):
        instance = elasticsearch.Elasticsearch("localhost")
        if instance.indices.exists(INDEX):
            instance.indices.delete(INDEX)

    def test_read_document_json_stream(self):
        iterable_data = read_input('{}/test_data_json_stream.json'.format(
                                   test_data_path), content_field="abstract")
        id, first_text = next(iter(iterable_data))
        self.assertEqual(first_text, self.solution_4)

    def test_read_documents_folder(self):
        loaded_dictionaries = read_input(
            '{}/test_data_folder_files'.format(test_data_path),
            content_field="abstract")
        id, first_text = next(iter(loaded_dictionaries))
        self.assertEqual(first_text, self.solution_1)

    def test_iter_documents_folder_gz(self):
        loaded_dictionaries = read_input(
            '{}/test_data_folder_files_gz'.format(test_data_path),
            content_field="abstract")
        id, first_text = next(iter(loaded_dictionaries))
        self.assertEqual(first_text, self.solution_1)

    def test_iter_large_json(self):
        iterable_data = read_input('{}/test_data_large_json.json'.format(test_data_path),
                                   content_field="text", json_prefix='item._source.isAuthorOf')
        id, first_text = next(iter(iterable_data))
        self.assertEqual(first_text, self.solution_3)

    def test_elastic_import(self):
        output_args = {'source': 'localhost',
                       'index': INDEX}
        # import data from file into known elastic server
        read_input('{}/test_data_json_stream.json'.format(
                   test_data_path), content_field="abstract",
                   output_type=ElasticSearchCorpus.class_key(),
                   output_args=output_args, synchronous_wait=30)
        iterable_data = read_input("localhost", source_type="elastic", content_field="abstract", index=INDEX)
        self.assertEquals(len(iterable_data), 100)


def test_bad_folder():
    nt.assert_raises(IOError, next, readers._iter_documents_folder("Frank"))


if __name__ == '__main__':
    unittest.main()
