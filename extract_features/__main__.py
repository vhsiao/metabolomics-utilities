__author__ = 'vivianhsiao'
import argparse
import sys
from os.path import dirname
sys.path.extend([dirname(dirname(__file__))])
from extract_features import *

if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_csv_path', help='The data file.')
    parser.add_argument('features_to_extract', help='A file containing features to be extracted; 1 per line.')
    parser.add_argument('--data_organized_in', default='rows', help='Is your data organized in rows or cols?')
    args = parser.parse_args()

    extract_features_from_file(args.data_csv_path, args.features_to_extract, data_organized_in=args.data_organized_in)
