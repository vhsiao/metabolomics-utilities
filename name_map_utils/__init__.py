__author__ = 'vhsiao'

import cPickle as pickle
import csv
import re
from os.path import dirname, join
default_map_pkl_path = join(dirname(dirname(__file__)), 'name_map_utils/maps/map.pkl')
default_temp_map_pkl_path = join(dirname(dirname(__file__)), 'name_map_utils/maps/temp_map.pkl')

# Constants
standard_name = 'sn'
pubchem = 'pc'
kegg = 'ke'
hmdb = 'hm'

class NameMap():
    name_map = dict()
    map_pkl_path = ''

    def __getitem__(self, item):
        return self.name_map.__getitem__(_clean_key(item))

    def __setitem__(self, key, value):
        self.name_map.__setitem__(_clean_key(key), value)

    def __contains__(self, item):
        return self.name_map.__contains__(_clean_key(item))

    def __len__(self):
        return self.name_map.__len__()

    def __str__(self):
        return '\n'.join(['{0}:{1}'.format(k, v) for k, v in self.name_map.items()])

    def clear(self):
        self.name_map = dict()
        self._commit()

    def add_mappings(self, name_map_csv_path):
        """
        :param name_map_csv_path: path/to/a CSV file containing mappings to add to the NameMap
        :return: None
        """
        ignore = ['', None, 'NA']
        update_method = lambda input_name_map: self.name_map.update(
            {k.lower(): {k2: v2 for k2, v2 in v.items() if v2 not in ignore} for k, v in input_name_map.items()})
        self._update_mappings(update_method, name_map_csv_path)

    def remove_mappings(self, name_map_csv_path):
        """
        :param name_map_csv_path: path/to/a CSV file containing mappings to remove from the NameMap
        :return: None
        """
        def update_method(input_name_map):
            wanted_keys = filter(
                lambda k: (k.lower() not in input_name_map) or (k in input_name_map and not input_name_map[k] == self.name_map[k]),
                self.name_map)
            self.name_map = {k: self.name_map[k] for k in wanted_keys}
        self._update_mappings(update_method, name_map_csv_path)

    def _update_mappings(self, update_method, name_map_csv_path):
        input_name_map = self.get_map_from_csv(name_map_csv_path)
        update_method(input_name_map)
        self._commit()

    def _commit(self):
        with open(self.map_pkl_path, 'w+') as map_pkl:
            pickle.dump(self.name_map, map_pkl)

    @classmethod
    def get_map_from_csv(self, name_map_csv_path):
        name_map_2 = dict()
        try:
            with open(name_map_csv_path, 'rU') as name_map_csv:
                reader = csv.DictReader(name_map_csv)
                try:
                    name_map_2 = {row['Query']: {
                        k1: row[k2] for k1, k2 in zip([standard_name, pubchem, kegg, hmdb],
                                                      ['Match', 'PubChem', 'KEGG', 'HMDB'])
                        if k2 in row
                    } for row in reader}
                except:
                    print('Had trouble adding entries from this name_map file. Double check the file {0}'
                          .format(name_map_csv_path))
                    raise
        except IOError:
            print('Name map at path {0} missing or invalid. Returning empty map.'.format(name_map_csv_path))
            raise
        return name_map_2

    def __init__(self, map_pkl_path=default_map_pkl_path):
        print "using name map at: {0}".format(map_pkl_path)
        with open(map_pkl_path, 'r') as map_pkl:
            self.map_pkl_path = map_pkl_path
            try:
                self.name_map = pickle.load(map_pkl)
            except EOFError:
                if map_pkl_path == default_map_pkl_path:
                    print "Name map not found at default location. Creating new."
                else:
                    print "No name map found at location. Using temp."
                    self.map_pkl_path = default_temp_map_pkl_path
        self._commit()


def prune(name_map_csv_path):
    """
    Goes through a name map csv file and removes entries that are not useful
    Examples of entries that will be removed:
        "Methionine","Methionine
        "methionine","Methionine
        "glucose.1","Glucose"
    :param name_map_csv_path:
    :return: None
    """
    with open(name_map_csv_path, 'rU') as name_map_csv:
        reader = csv.DictReader(name_map_csv)
        keep = filter(lambda rd: not _redundant_name_map_csv_entry(rd),
                      reader)
    with open(name_map_csv_path, 'w+') as name_map_csv:
        writer = csv.DictWriter(name_map_csv, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(keep)

def _redundant_name_map_csv_entry(rowdict):
    redundant = False
    if rowdict['Query'].lower() == rowdict['Match'].lower():
        redundant = True
    elif re.search('\.[0-9]+$', rowdict['Query']):
        redundant = True
    elif rowdict['Match'] == 'NA':
        redundant = True
    return redundant

def _clean_key(key):
        return key.strip().replace(',', ' ').lower()
