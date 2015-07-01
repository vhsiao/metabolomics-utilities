__author__ = 'vhsiao'

import cPickle as pickle
import csv
from os.path import dirname, join

default_map_pkl_path = join(dirname(dirname(__file__)), 'name_map_utils/maps/map.pkl')
class NameMap():
    name_map = dict()
    map_pkl_path = ''

    def __getitem__(self, item):
        return self.name_map.__getitem__(item)

    def __setitem__(self, key, value):
        self.name_map.__setitem__(key, value)

    def __contains__(self, item):
        return self.name_map.__contains__(item)

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
            {k: v for k, v in input_name_map.items() if v not in ignore})
        self._update_mappings(update_method, name_map_csv_path)

    def remove_mappings(self, name_map_csv_path):
        """
        :param name_map_csv_path: path/to/a CSV file containing mappings to remove from the NameMap
        :return: None
        """
        def update_method(input_name_map):
            wanted_keys = filter(
                lambda k: (k not in input_name_map) or (k in input_name_map and not input_name_map[k] == self.name_map[k]),
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
                    name_map_2 = {row['Query']: row['Match'] for row in reader}
                except:
                    print('Had trouble adding entries from this name_map file. Double check the file {0}'
                          .format(name_map_csv_path))
                    raise
        except IOError:
            print('Name map at path {0} missing or invalid. Returning empty map.'.format(name_map_csv_path))
            raise
        return name_map_2

    def __init__(self, map_pkl_path=default_map_pkl_path):
        try:
            with open(map_pkl_path, 'r') as map_pkl:
                self.map_pkl_path = map_pkl_path
                self.name_map = pickle.load(map_pkl)
            pass
        except EOFError:
            pass
        except IOError:
            self.map_pkl_path = 'temp_map.pkl'
            self._commit()
