import argparse
import sys
from os import listdir
from os.path import dirname, isfile, abspath
sys.path.extend([dirname(dirname(__file__))])

from name_map_utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    group_dir_vs_file = parser.add_mutually_exclusive_group()
    group_add_vs_remove = parser.add_mutually_exclusive_group()

    group_add_vs_remove.add_argument('-d', action='store_true', help='delete mappings found in a single file.')
    group_add_vs_remove.add_argument('-a', action='store_true', help='add mappings found in a single file.')

    group_dir_vs_file.add_argument(
        '--use-file', metavar='name_map_file', help='The file to add or remove mappings from.')

    group_dir_vs_file.add_argument('--find-in-dir', metavar='name_map_dir',
                                   default='{0}/map_csv'.format(dirname(__file__)),
                                   help='Add or remove all files found in dir.')

    args = parser.parse_args()

    current_map = NameMap()

    if args.name_map_file:
        name_map_files = [args.name_map_file]
    elif args.name_map_dir:
        name_map_files = [f for f in listdir(args.name_map_dir) if isfile(abspath(f))]
    else:
        name_map_files = []
        print('There are currently {0} values in the name map.'.format(len(current_map)))

    for f in name_map_files:
        if args.a:
            current_map.add_mappings(f)
        elif args.d:
            current_map.remove_mappings(f)
