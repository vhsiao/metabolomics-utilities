__author__ = 'vhsiao'

import unittest
from os.path import abspath
from prep_dataset_for_metaboanalyst import *
from itertools import izip_longest

class SimpleTestPrepDatasetForMetaboanalyst(unittest.TestCase):
    def setUp(self):
        self.map_csv_path = 'test_data/test_map_csv/test_map_0.csv'
        self.map_pkl_path = 'test_data/test_maps/test_map_0.pkl'
        self.name_map = NameMap(abspath(self.map_pkl_path))
        self.name_map.add_mappings(self.map_csv_path)

    def tearDown(self):
        self.name_map.clear()

    def test_standardize_compound_names(self):
        print '\n\ntest_standardize_compound_names'
        original_fieldnames = ['alanine', 'hydroxyproline', 'sarcosine', 'glutamine', 'anthranilate', 'alanine-nega', 'bunny']
        result = standardized_compound_names(original_fieldnames, self.map_pkl_path)
        self.assertEqual(result,
                    ['Alanine', '4-Hydroxyproline', 'Sarcosine', 'L-Glutamine', '2-Aminobenzoic acid', 'Alanine', 'bunny'])

        original_fieldnames = ['alanine', 'hydroxyproline', '4-Hydroxyproline', 'glutamine']
        result = standardized_compound_names(original_fieldnames, self.map_pkl_path)
        self.assertEqual(result,
                         ['Alanine', '4-Hydroxyproline', '4-Hydroxyproline', 'L-Glutamine']
        )

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
        map_pkl_path = 'test_data/test_maps/test_map_0.pkl'
        arg_sets = [['test_data/test_datasets_csv/test_dataset_0_cols.csv', 4, 0, 'cols', 1, map_pkl_path],
                    ['test_data/test_datasets_csv/test_dataset_0_rows.csv', 4, 0, 'rows', 1, map_pkl_path]]
        for arg_set in arg_sets:
            prep_dataset(*arg_set)
            try:
                diff = compare_csv_contents('{0}_MA{1}'.format(*splitext(arg_set[0])),
                                            'test_data/test_datasets_csv/expected_prepared_test_dataset_0.csv')
                self.assertEquals(len(diff), 0)
            except AssertionError:
                raise AssertionError('File: {0}\n diff:\n{1}'.format(arg_set[0], diff))

class TestPrepDatasetForMetaboanalyst(unittest.TestCase):
    def setUp(self):
        self.map_csv_path = 'test_data/test_map_csv/test_map_1.csv'
        self.map_pkl_path = 'test_data/test_maps/test_map_1.pkl'
        self.name_map = NameMap(abspath(self.map_pkl_path))
        self.name_map.add_mappings(self.map_csv_path)

    def test_standardize_compound_names(self):
        print '\n\ntest_standardize_compound_names'
        original_fieldnames = ['cystathione', 'proline', 'cholate', 'alanine', 'Alpha-ketoisovaleric acid',
                               'deoxyribose-phosphate']
        result = standardized_compound_names(original_fieldnames, self.map_pkl_path, id_type=kegg)
        self.assertEqual(result, ['C02291', 'C00148', 'C00695', 'C01401', 'C00141', 'deoxyribose-phosphate'])

    def test_prep_dataset(self):
        print '\n\ntest_prep_dataset'
        map_pkl_path = 'test_data/test_maps/test_map_1.pkl'
        arg_sets = [['test_data/test_datasets_csv/test_dataset_1_cols.csv', 1, None, 'cols', None, map_pkl_path,
                     True, kegg],
                    ['test_data/test_datasets_csv/test_dataset_1_rows.csv', 1, None, 'rows', None, map_pkl_path,
                     True, kegg]]
        for arg_set in arg_sets:
            prep_dataset(*arg_set)
            try:
                diff = compare_csv_contents('{0}_MA{1}'.format(*splitext(arg_set[0])),
                                            'test_data/test_datasets_csv/expected_prepared_test_dataset_1.csv')
                self.assertEquals(len(diff), 0)
            except AssertionError:
                raise AssertionError('File: {0}\n diff:\n{1}'.format(arg_set[0], diff))

def compare_csv_contents(csv_file1, csv_file2):
    with open(csv_file1, 'rU') as file1:
        reader_file1 = csv.reader(file1)
        with open(csv_file2, 'rU') as file2:
            reader_file2 = csv.reader(file2)

            diff = []
            row = 0
            col = 0

            for line in izip_longest(reader_file1, reader_file2):
                row += 1
                try:
                    pairs = zip(*line)
                    for val1, val2 in pairs:
                        col += 1
                        if not val1 == val2:
                            diff.append('R{row} C{col}: {val1} differs from {val2}'.format(
                                row=row, col=col, val1=val1, val2=val2
                            ))
                except TypeError:
                    print 'Size mismatch! {0}'.format(line)
    return diff


