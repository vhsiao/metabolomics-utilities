__author__ = 'vhsiao'

import unittest
from name_map_utils import NameMap

class TestNameMapUtils(unittest.TestCase):
    def setUp(self):
        self.name_map = NameMap('test/test_maps/test_map.pkl')
        self.name_map['existing entry 1'] = 'foo'
        self.name_map['existing entry 2'] = 'bar'
        self.name_map._commit()

    def tearDown(self):
        pass

    def test_get_map_from_csv(self):
        map = self.name_map.get_map_from_csv('test/test_csv/test_map_tiny.csv')
        self.assertDictEqual(map, {'speshul': 'special', 'weird': 'unicorn'})

    def test_add_mappings(self):
        self.name_map.add_mappings('test/test_csv/test_map_small.csv')
        self.assertEqual(self.name_map['speshul'], 'special')
        self.assertEqual(self.name_map['speshol'], 'special')
        self.assertEqual(self.name_map['irregardless of'], 'regardless of')
        self.assertEqual(self.name_map['tomahto'], 'tomato')
        self.assertEqual(self.name_map['existing entry 1'], 'foo')
        self.assertEqual(self.name_map['existing entry 2'], 'bar')

    def test_remove_mappings(self):
        self.name_map.add_mappings('test/test_csv/test_map_small.csv')
        self.name_map.remove_mappings('test/test_map_tiny.csv')
        self.assertEqual(self.name_map['speshol'], 'special')
        self.assertEqual('speshul' in self.name_map, False)

