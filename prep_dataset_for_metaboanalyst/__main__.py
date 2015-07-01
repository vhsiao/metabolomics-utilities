import argparse
import sys
from os.path import dirname
sys.path.extend([dirname(dirname(__file__))])

from prep_dataset_for_metaboanalyst import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_csv', metavar='data.csv')
    parser.add_argument('num_id_entries', default=4, metavar='Number of identification entries', type=int,
                        help='How many initial entries in the file contain ID information for the sample?')
    parser.add_argument('label_info_entry_idx', default=0, metavar='Column with label info', type=int,
                        help='Which initial entry in the file contains the label info? (eg: wild-type)')
    parser.add_argument('litter_info_entry_idx', default=1, metavar='Column with litter info', type=int,
                        help='Which initial entry in the file contains the litter info? (eg: litter 1)')
    parser.add_argument('data_organized_in', default='cols', metavar='Data organization',
                        help='Is the data organized in rows or cols?')
    args = parser.parse_args()
    prep_dataset(args.data_csv, args.num_id_entries, args.label_info_entry_idx, args.litter_info_entry_idx)
    print 'All done. Your prepped data is in the same folder as the source data. Cool beans.'
