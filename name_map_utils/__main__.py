import argparse
import sys
from os import listdir
from os.path import dirname, basename, join
sys.path.extend([dirname(dirname(__file__))])

import name_map_utils
from name_map_utils import NameMap

# TODO extend this module to generate a map to PubChem CIDs for better accuracy.

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    group_dir_vs_file = parser.add_mutually_exclusive_group()
    group_action = parser.add_mutually_exclusive_group()

    group_action.add_argument('-d', action='store_true', help='Delete mappings found in a single file')
    group_action.add_argument('-a', action='store_true', help='Add mappings found in a single file.')
    group_action.add_argument('--prune_csv', action='store_true', help='Prune input files.')

    group_dir_vs_file.add_argument(
        '--use_file', metavar='name_map_file', help='The file to add or remove mappings from.')

    group_dir_vs_file.add_argument('--find-in-dir', metavar='name_map_dir',
                                   default='{0}/map_csv'.format(dirname(__file__)),
                                   help='Add or remove all files found in dir.')

    parser.add_argument('--clear_first', action='store_true', default=False,
                        help='Use this flag if you want to clear the existing name map first.')


    args = parser.parse_args()
    name_map_files = []

    if args.use_file:
        use_file = join(args.find_in_dir, args.use_file)
        print "Incorporating file {0}".format(use_file)
        name_map_files = [use_file]
    elif args.find_in_dir:
        print "Incorporating all name map files in {0}.".format(args.find_in_dir)
        name_map_files = [join(args.find_in_dir, f) for f in listdir(args.find_in_dir) if f.endswith('.csv')]

        # Find "manual" csv files and move them to the end so that their contents take priority.
        index_of_manual = filter(lambda j: 'manual' in basename(name_map_files[j]), range(len(name_map_files)))
        index_of_manual.sort(reverse=True)
        for i in index_of_manual:
            name_map_files.append(name_map_files.pop(i))

    current_map = NameMap()

    if args.clear_first:
        current_map.clear()

    for f in name_map_files:
        print f
        if args.a:
            current_map.add_mappings(f)
        elif args.d:
            current_map.remove_mappings(f)
        elif args.prune_csv:
            name_map_utils.prune(f)
        else:
            print('There are currently {0} values in the name map.'.format(len(current_map)))

    print str(len(name_map_files)) + ' file(s) processed.'
