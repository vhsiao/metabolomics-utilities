__author__ = 'vhsiao'

import cPickle as pickle
import csv
import argparse

class NameMap():
    name_map = dict()
    map_pkl_path = ''

    def __getitem__(self, item):
        return self.name_map.__getitem__(item)

    def __setitem__(self, key, value):
        self.name_map.__setitem__(key, value)

    def __contains__(self, item):
        return self.name_map.__contains__(item)

    def add_mappings(self, name_map_csv_path=None):
        """
        :param name_map_csv_path: path/to/a CSV file containing mappings to add to the NameMap
        :return: None
        """
        update_method = lambda input_name_map: self.name_map.update(input_name_map)
        self._update_mappings(update_method, name_map_csv_path)

    def remove_mappings(self, name_map_csv_path=None):
        """
        :param name_map_csv_path: path/to/a CSV file containing mappings to remove from the NameMap
        :return: None
        """
        update_method = lambda input_name_map: filter(lambda x: x not in input_name_map, self.name_map)
        self._update_mappings(update_method, name_map_csv_path)

    def _update_mappings(self, update_method, name_map_csv_path=None):
        input_name_map = self.get_map_from_csv(name_map_csv_path)
        self.name_map = update_method(input_name_map)
        self._commit()

    def _commit(self):
        with open(self.map_pkl_path, 'w+') as map_pkl:
            pickle.dump(self.name_map, map_pkl)

    @classmethod
    def get_map_from_csv(self, name_map_csv_path=None):
        name_map_2 = None
        try:
            with open(name_map_csv_path) as name_map_csv:
                reader = csv.DictReader(name_map_csv)
                try:
                    name_map_2 = {row['Query']: row['Match'] for row in reader}
                except:
                    print('Had trouble adding entries from this name_map file. Double check the file {0}'
                          .format(name_map_csv_path))
        except:
            print('No name map was given.')
        return name_map_2

    def __init__(self, map_pkl_path='maps/map.pkl'):
        try:
            with open(map_pkl_path, 'w+') as map_pkl:
                self.name_map = pickle.load(map_pkl)
            self.map_pkl_path = map_pkl_path
        except:
            self.name_map = pickle.loads('')
            self.map_pkl_path = 'temp_map.pkl'

if __name__ == 'main':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', action = 'store_true')
    group.add_argument('-a', action = 'store_true')
    parser.add_argument('New name map', metavar='new_name_map')
    args = parser.parse_args()

    current_map = NameMap()

    if args.a:
        current_map.add_mappings(args.new_name_map)
    elif args.d:
        current_map.remove_mappings(args.new_name_map)
    else:
        print('There are currently {0} values in the name map.'.format(current_map.name_map))