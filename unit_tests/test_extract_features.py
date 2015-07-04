import unittest
from itertools import izip_longest
from extract_features import *

class SimpleTestExtractFeatures(unittest.TestCase):

    def test_extract_features(self):
        cases = [
            {
                'csv': 'test_data/test_datasets_csv/test_dataset_tiny.csv',
                'features': 'test_data/test_feature_lists/list_tiny',
                'exp_path': 'test_data/test_datasets_csv/expected_test_dataset_tiny_extr_list_tiny.csv'
            },
            {
                'csv': 'test_data/test_datasets_csv/test_dataset_0_rows_MA.csv',
                'features': 'test_data/test_feature_lists/list_0',
                'exp_path': 'test_data/test_datasets_csv/expected_test_dataset_0_rows_MA_extr_list_0.csv'
            }
        ]

        for case in cases:
            data_csv_path, features_to_extract_path, expected_path \
                = [case[k] for k in ['csv', 'features', 'exp_path']]
            actual_path = '{orig_dataset}_extr_{features}'.format(orig_dataset=splitext(data_csv_path)[0],
                                                        features=split(features_to_extract_path)[1])
            extract_features_from_file(data_csv_path, features_to_extract_path)
            with open(expected_path, 'rU') as expected:
                reader_e = csv.reader(expected)
                with open(actual_path, 'rU') as actual:
                    reader_a = csv.reader(actual)
                    for e, a in izip_longest(reader_e, reader_a):
                        self.assertEquals(e, a)
