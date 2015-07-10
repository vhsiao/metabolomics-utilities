__author__ = 'vhsiao'

import unittest
from name_map_utils import NameMap
from name_map_utils import standard_name, pubchem, hmdb, kegg
import cPickle as pickle

class SimpleTestNameMapUtils(unittest.TestCase):
    def setUp(self):
        self.name_map = NameMap('test_data/test_maps/test_map.pkl')
        self.name_map.clear()
        self.name_map['existing entry 1'] = {standard_name: 'foo'}
        self.name_map['existing entry 2'] = {standard_name: 'bar'}
        self.name_map._commit()

    def tearDown(self):
        pass

    def test_get_map_from_csv(self):
        result_map = self.name_map.get_map_from_csv('./test_data/test_map_csv/test_map_tiny.csv')
        self.assertTrue(contains_only(result_map, {'speshul': {standard_name: 'special'},
                                                   'tomahto': {standard_name: 'tomato'},
                                                   'weird': {standard_name: 'unicorn'},
                                                   'existing entry 1': {standard_name: 'not foo'}}))

    def test_add_mappings(self):
        self.name_map.add_mappings('./test_data/test_map_csv/test_map_small.csv')
        self.assertEqual(self.name_map['speshul'][standard_name], 'special')
        self.assertEqual(self.name_map['speshol'][standard_name], 'special')
        self.assertEqual(self.name_map['irregardless of'][standard_name], 'regardless of')
        self.assertEqual(self.name_map['tomahto'][standard_name], 'tomato')
        self.assertEqual(self.name_map['existing entry 1'][standard_name], 'foo')
        self.assertEqual(self.name_map['existing entry 2'][standard_name], 'bar')
        with open(self.name_map.map_pkl_path) as map_pkl:
            loaded_map = pickle.load(map_pkl)


    def test_remove_mappings(self):
        self.name_map.add_mappings('test_data/test_map_csv/test_map_small.csv')
        self.name_map.remove_mappings('test_data/test_map_csv/test_map_tiny.csv')
        self.assertEqual(self.name_map['speshol'][standard_name], 'special')
        self.assertFalse('speshul' in self.name_map)
        with open(self.name_map.map_pkl_path) as map_pkl:
            loaded_map = pickle.load(map_pkl)
            self.assertTrue(contains_only(loaded_map, {
                'speshol': {standard_name: 'special'},
                'irregardless of': {standard_name: 'regardless of'},
                'existing entry 1': {standard_name: 'foo'},
                'existing entry 2': {standard_name: 'bar'}
            }))

    def test_clear(self):
        self.name_map.clear()
        self.assertEqual(len(self.name_map), 0)
        with open(self.name_map.map_pkl_path) as map_pkl:
            loaded_map = pickle.load(map_pkl)
            self.assertEqual(len(loaded_map), 0)

class TestNameUtils(unittest.TestCase):
    def setUp(self):
        self.name_map = NameMap('test_data/test_maps/test_map_0.pkl')

    def test_add_mappings1(self):
        self.name_map.add_mappings('test_data/test_map_csv/test_map_0.csv')
        print self.name_map
        self.assertEqual(self.name_map['alanine'][standard_name], 'Alanine')
        self.assertEqual(self.name_map['anthranilate'][standard_name], '2-Aminobenzoic acid')

    def test_add_mappings2(self):
        self.name_map.add_mappings('test_data/test_map_csv/test_map_1.csv')
        print self.name_map
        self.assertEqual(self.name_map['cystathionine'],
                         {standard_name: 'L-Cystathionine', hmdb: 'HMDB00099', pubchem: '439258', kegg: 'C02291'})

        self.assertEqual(self.name_map['proline'],
                         {standard_name: 'L-Proline', hmdb: 'HMDB00162', pubchem: '145742', kegg: 'C00148'})

        self.assertEqual(self.name_map['alanine'],
                         {standard_name: 'Alanine', hmdb: 'METPA0179', kegg: 'C01401'})

    def test_remove_mappings(self):
        pass

def contains_only(dict1, dict2):
    '''
    Tests whether dict1 contains only contents of dict2
    :param dict1: Containing dict
    :param dict2: Contained dict
    :return:  True iff dict1 contains all the entries in dict2 and all other entries of dict1 are falsey
    '''
    only = all(map(lambda k: dict1[k] == dict2[k] if k in dict2 else not dict1[k], dict1.keys()))
    return only

if __name__ == '__main__':
    unittest.main()
