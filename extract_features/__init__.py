__author__ = 'vivianhsiao'

import csv
from os.path import split, splitext

def extract_features_from_file(data_csv_path, features_to_extract_path, data_organized_in='rows'):
    with open(features_to_extract_path) as features:
        feat_list = ['Sample', 'Label'] + [line.strip() for line in features.readlines()]
        print 'feature list found:'
        print feat_list
    with open(data_csv_path, 'rU') as data_csv:
        reader = csv.DictReader(data_csv)
        dataset = [rowdict for rowdict in reader]
        keep = map(lambda rowdict: {entry: rowdict[entry] for entry in rowdict if entry in feat_list},
                      dataset)
    dest_path = '{orig_dataset}_extr_{features}'.format(orig_dataset=splitext(data_csv_path)[0],
                                                        features=split(features_to_extract_path)[1])
    with open(dest_path, 'w+') as dest:
        writer = csv.DictWriter(dest, feat_list)
        writer.writeheader()
        writer.writerows(keep)
