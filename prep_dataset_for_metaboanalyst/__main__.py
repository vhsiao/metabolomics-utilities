import argparse
import sys
from os.path import dirname
sys.path.extend([dirname(dirname(__file__))])

from prep_dataset_for_metaboanalyst import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data.csv', metavar='data_csv')
    parser.add_argument('Number of identification entries', default=4, metavar='num_id_entries',
                        help='How many initial entries in the file contain ID information for the sample?')
    parser.add_argument('Column with label info', default=0, metavar='label_info_entry_idx',
                        help='Which initial entry in the file contains the label info? (eg: wild-type)')
    parser.add_argument('Column with litter info', default=1, metavar='litter_info_entry_idx',
                        help='Which initial entry in the file contains the litter info? (eg: litter 1)')
    parser.add_argument('Data organization', default='cols', metavar='data_organized_in',
                       help='Is the data organized in rows or cols?')
    args = parser.parse_args()
    prep_dataset(args.data_csv, args.num_id_entries, args.label_info_entry_idx, args.litter_info_entry_idx)

