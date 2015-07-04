import argparse
import sys
from os.path import dirname
sys.path.extend([dirname(dirname(__file__))])

from prep_dataset_for_metaboanalyst import *

# TODO extend this module to generate a map to PubChem CIDs for better accuracy.
# TODO add feature to extract features of interest from a file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_csv', metavar='data.csv')
    parser.add_argument('num_id_entries', default=4, metavar='Number of identification entries', type=int,
                        help='How many initial entries in the file contain ID information for the sample?')
    parser.add_argument('label_info_entry_idx', metavar='Row/column with label info', type=int,
                        help='Which initial entry in the file contains the label info? (eg: wild-type)')

    parser.add_argument('--data_organized_in', default='cols', metavar='Data organization',
                        help='Is the data organized in rows or cols?')
    parser.add_argument('--litter_info_entry_idx', default=None, metavar='Row/column with litter info', type=int,
                        help='Which initial entry in the file contains the litter info? (eg: litter 1)')
    args = parser.parse_args()

    prep_dataset(args.data_csv, num_metadata_fields=args.num_id_entries,data_organized_in=args.data_organized_in,
                 label_info_field_idx=args.label_info_entry_idx, litter_info_field_idx=args.litter_info_entry_idx)
    print 'All done. Your prepped data is in the same folder as the source data. Cool beans.'
