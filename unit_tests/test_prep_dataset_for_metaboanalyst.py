__author__ = 'vhsiao'

import unittest
from name_map_utils import NameMap
from prep_dataset_for_metaboanalyst import *

class SimpleTestPrepDatasetForMetaboanalyst(unittest.TestCase):
    def setUp(self):
        self.map_csv_path = 'test_data/test_map_csv/test_map_0.csv'
        self.map_pkl_path = 'test_data/test_map/test_map_0.pkl'
        self.name_map = NameMap(self.map_pkl_path)
        self.name_map.add_mappings(self.map_csv_path)

    def tearDown(self):
        self.name_map.clear()

    def test_standardize_compound_names(self):
        print '\n\ntest_standardize_compound_names'
        original_fieldnames = ['alanine', 'hydroxyproline', 'sarcosine', 'glutamine', 'anthranilate', 'bunny']
        result = standardize_compound_names(original_fieldnames, self.map_pkl_path)
        self.assertEqual(result,
                    ['Alanine', '4-Hydroxyproline', 'Sarcosine', 'L-Glutamine', '2-Aminobenzoic acid', 'bunny'])

    def test_infer_label(self):
        print '\n\ntest_infer_label'
        self.assertEquals(infer_label('062514Q\nEMMut1'), 'ho')
        self.assertEquals(infer_label('062514Q\nEMHET3'), 'he')
        self.assertEquals(infer_label('062514Q\nHET'), 'he')
        self.assertEquals(infer_label('062514Q\nEMWT6'), 'wt')
        self.assertEquals(infer_label('062514Q\nWTHET'), 'wt')
        self.assertEquals(infer_label('1234567'), 'unknown')

    def test_consolidate_sample_metadata(self):
        print '\n\ntest_consolidate_sample_metadata'
        sample_metadata = [
            ['123456\nVH1', '123456\nVH2', '123456\nVH3'],
            ['Litter1', 'Litter1', 'Litter2'],
            ['VHWT', 'VHMut', 'VHHet']
        ]

        consolidated_metadata = consolidate_sample_metadata(sample_metadata, 2, 1)
        self.assertEquals(consolidated_metadata[0],
                          ['0_wt_L1', '1_ho_L1', '2_he_L2']
                          )
        self.assertEquals(consolidated_metadata[1],
                          [1, 3, 2]
                          )

    def test_prep_dataset(self):
        pass






