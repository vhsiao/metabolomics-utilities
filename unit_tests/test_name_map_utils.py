__author__ = 'vhsiao'

import unittest
from name_map_utils import NameMap
import cPickle as pickle

class SimpleTestNameMapUtils(unittest.TestCase):
    def setUp(self):
        self.name_map = NameMap('test_data/test_maps/test_map.pkl')
        self.name_map.clear()
        self.name_map['existing entry 1'] = 'foo'
        self.name_map['existing entry 2'] = 'bar'
        self.name_map._commit()

    def tearDown(self):
        pass

    def test_get_map_from_csv(self):
        result_map = self.name_map.get_map_from_csv('./test_data/test_csv/test_map_tiny.csv')
        self.assertDictEqual(result_map, {'speshul': 'special', 'tomahto': 'tomato', 'weird': 'unicorn', 'existing entry 1': 'not foo'})

    def test_add_mappings(self):
        self.name_map.add_mappings('./test_data/test_csv/test_map_small.csv')
        self.assertEqual(self.name_map['speshul'], 'special')
        self.assertEqual(self.name_map['speshol'], 'special')
        self.assertEqual(self.name_map['irregardless of'], 'regardless of')
        self.assertEqual(self.name_map['tomahto'], 'tomato')
        self.assertEqual(self.name_map['existing entry 1'], 'foo')
        self.assertEqual(self.name_map['existing entry 2'], 'bar')
        with open(self.name_map.map_pkl_path) as map_pkl:
            loaded_map = pickle.load(map_pkl)


    def test_remove_mappings(self):
        self.name_map.add_mappings('test_data/test_csv/test_map_small.csv')
        self.name_map.remove_mappings('test_data/test_csv/test_map_tiny.csv')
        self.assertEqual(self.name_map['speshol'], 'special')
        self.assertFalse('speshul' in self.name_map)
        with open(self.name_map.map_pkl_path) as map_pkl:
            loaded_map = pickle.load(map_pkl)
            self.assertEqual(loaded_map, {
                'speshol': 'special',
                'irregardless of': 'regardless of',
                'existing entry 1': 'foo',
                'existing entry 2': 'bar'
            })

    def test_clear(self):
        self.name_map.clear()
        self.assertEqual(len(self.name_map), 0)
        with open(self.name_map.map_pkl_path) as map_pkl:
            loaded_map = pickle.load(map_pkl)
            self.assertEqual(len(loaded_map), 0)

if __name__ == '__main__':
    unittest.main()
