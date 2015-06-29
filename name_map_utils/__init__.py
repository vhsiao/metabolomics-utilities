__author__ = 'vhsiao'

import cPickle
import csv
import argparse

class NameMap():
    name_map = dict()
    map_pkl = 'maps/map.pkl'

    def __getitem__(self, item):
        return self.name_map.__getitem__(item)

    def __setitem__(self, key, value):
        self.name_map.__setitem__(key, value)

    def add_mappings(self, metaboanalyst_name_map_csv=None):
        input_name_map = self.get_map_from_csv(metaboanalyst_name_map_csv)
        self.name_map.update(input_name_map)
        self._commit()

    def remove_mappings(self, metaboanalyst_name_map_csv=None):
        input_name_map = self.get_map_from_csv(metaboanalyst_name_map_csv)
        self.name_map = filter(lambda x: x not in input_name_map, self.name_map)
        self._commit()

    def _commit(self):
        cPickle.dump(self.name_map, self.map_pkl)

    @classmethod
    def get_map_from_csv(self, metaboanalyst_name_map_csv=None):
        name_map_2 = None
        try:
            with open(metaboanalyst_name_map_csv) as name_map_csv:
                reader = csv.DictReader(name_map_csv)
                try:
                    name_map_2 = {row['Query']: row['Match'] for row in reader}
                except:
                    print('Had trouble adding entries from this name_map file. Double check the file {0}'
                          .format(metaboanalyst_name_map_csv))
        except:
            print('No name map was given.')
        return name_map_2

    def __init__(self):
        try:
            self.name_map = cPickle.load(self.map_pkl)
        except:
            self.name_map = None

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