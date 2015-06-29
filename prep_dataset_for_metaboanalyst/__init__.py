__author__ = 'vhsiao'

import csv
import argparse
from name_map_utils import NameMap

label_map = {
    'wt': ['wt', 'wild'],  # wild type
    'he': ['het'],  # heterozygote
    'ho': ['hom', 'mut']  # homozygote
    }

label_numbers = {'wt': 1, 'he': 2, 'ho': 3, 'unknown': 99}

def prep_dataset(data_csv_path, num_metadata_rows, label_info_row_idx, litter_info_row_idx, data_organized_in='rows'):
    """
    Prep dataset for metaboanalyst.
    :param data_csv_path: Path to a data csv file. Assumes the samples are in rows.
    :param num_metadata_rows: The number of metadata rows in the data file.
    :param label_info_row_idx: The index of the row containing information about sample group labels.
    :param litter_info_row_idx: The index of the row containing information about sample litter.
    :return: None
    """
    #TODO
    with open(data_csv_path) as source:
        with open('{0}_{1}'.format('metaboanalyst', data_csv_path)) as destination:
            reader = csv.DictReader(source)

            # Grab the sample metadata entries from the source file
            sample_metadata = []
            for i in range(num_metadata_rows):
                sample_metadata.append(source.readline())

            sample_names, sample_labels = consolidate_sample_metadata(sample_metadata, label_info_row_idx, litter_info_row_idx)

            # Standardize compound names using the name map
            standardized_compound_names = standardize_compound_names(reader.fieldnames[num_metadata_rows:])
            standardized_compound_names = [''].extend(standardized_compound_names)
            writer = csv.DictWriter(destination, fieldnames=standardized_compound_names)
            writer.writeheader()
            writer.writerow(['Sample'].extend(sample_names))
            writer.writerow(['Label'].extend(sample_labels))
            writer.writerows(source.readlines())

def consolidate_sample_metadata(sample_metadata, label_info_entry_idx, litter_info_entry_idx):
    """
    Infer good sample names from sample metadata entries
    :param sample_metadata: A 2-D list. Each row is a list of one metadata field for each sample.
    Example: [['WT', 'HET'],['litter2', 'litter1'], ['12345', '67890']]
    :param label_info_entry_idx: Index of the metadata field containing label information. Example: 0
    :param litter_info_entry_idx: Index of the metadata field containing litter information. Example: 1
    :return: A list of good sample names and a list of labels (each entry corresponds to 1 sample).
    Example: ['L1_wt', 'L2_het'], [1, 2]
    """
    try:
        label_info = sample_metadata[label_info_entry_idx]
    except IndexError:
        print "Invalid label info entry"
        raise

    # Litter information
    try:
        litter_info = sample_metadata[litter_info_entry_idx]
    except IndexError:
        print "Invalid litter info entry. Litter info will not be included in the sample id."
        litter_info = None
    except:
        raise

    sample_ids = []
    sample_labels = []
    for i in range(len(label_info)):
        label = infer_label(label_info[i])
        litter = ''
        if litter_info:
            litter = 'L' + ''.join([c for c in litter_info[i] if c.isdigit()])
        id = '_'.join([str(i), label, litter])
        sample_ids.append(id)
        sample_labels.append(label_numbers[label])
    return sample_ids, sample_labels

def infer_label(label_entry):
    """
    :param label_entry: Contents of the field from which to infer a label
    :return: Label inferred from label_entry
    """
    possible_labels = []
    label_entry_l = label_entry.lower()
    for label in label_map:
        is_label = any(map(lambda x: label_entry_l.__contains__(x), label_map[label]))
        if is_label:
            possible_labels.append(label)
    if possible_labels:
        if len(possible_labels) > 1:
            print 'This label could be: ',
            print possible_labels
            print 'Choosing {0}'.format(possible_labels[0])
        label = possible_labels[0]
    else:
        print 'Didn\'t find label in entry {0}.'.format(label_entry),
        print 'Setting to unknown (99)'
        label = 'unknown'
    return label

def standardize_compound_names(original_fieldnames, map_pkl_path='maps/map.pkl'):
    """
    :param original_fieldnames: A list of original field names to be standardized
    :param map_pkl_path: Path to a pkl file containing mappings used to standardize the names
    :return: A list of standardized field names
    """
    name_map = NameMap(map_pkl_path=map_pkl_path)
    return [name_map[field] if field in name_map else field for field in original_fieldnames]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data.csv', metavar='data_csv')
    parser.add_argument('Number of identification entries', default=4, metavar='num_id_entries',
                        description='How many initial entries in the file contain ID information for the sample?')
    parser.add_argument('Column with label info', default=0, metavar='label_info_entry_idx',
                        description='Which initial entry in the file contains the label info? (eg: wild-type)')
    parser.add_argument('Column with litter info', default=1, metavar='litter_info_entry_idx',
                        description='Which initial entry in the file contains the litter info? (eg: litter 1)')
    args = parser.parse_args()
    prep_dataset(args.data_csv, args.num_id_entries, args.label_info_entry_idx, args.litter_info_entry_idx)