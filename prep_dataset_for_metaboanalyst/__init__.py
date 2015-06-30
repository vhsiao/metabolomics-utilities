__author__ = 'vhsiao'

import csv
import argparse
from os.path import splitext, dirname
import sys
sys.path.extend([dirname(dirname(__file__))])

from name_map_utils import NameMap

label_map = {
    'wt': ['wt', 'wild'],  # wild type
    'he': ['het'],  # heterozygote
    'ho': ['hom', 'mut']  # homozygote
}

label_numbers = {'wt': 1, 'he': 2, 'ho': 3, 'unknown': 99}

def prep_dataset(data_csv_path, num_metadata_fields, label_info_field_idx, litter_info_field_idx, data_organized_in='cols'):
    """
    Prep dataset for metaboanalyst.
    :param data_csv_path: Path to a data csv file.
    :param num_metadata_fields: The number of metadata rows in the data file.
    :param label_info_field_idx: The index of the row containing information about sample group labels.
    :param litter_info_field_idx: The index of the row containing information about sample litter.
    :param data_organized_in: Options: 'rows' or 'cols'. Specifies whether data is in rows or columns.
    Defaults to 'cols'.
    :return: None
    """

    if data_organized_in not in ['rows', 'cols']:
        raise Exception('Invalid option {0} for data_organized_in.'.format(data_organized_in))

    with open(data_csv_path, 'rU') as source:
        reader = csv.reader(source)
        dataset = [line for line in reader]
        if data_organized_in == 'rows':
            dataset = zip(*dataset)  # first pivot data if it is in rows. Now each column should contain one sample.

        # Grab the sample metadata entries from the source file. Discard the first column ('Sample Name', etc).
        sample_metadata = [row[1:] for row in dataset[:num_metadata_fields]]
        sample_names, sample_labels = consolidate_sample_metadata(
            sample_metadata, label_info_field_idx, litter_info_field_idx)

        # Standardize compound names using the name map
        compound_names = [row[0] for row in dataset[num_metadata_fields:]]
        standardized_compound_names = standardize_compound_names(compound_names)

        # Clean up the data values
        values = zip(*[row[1:] for row in dataset[num_metadata_fields:]])
        cleaned_values = clean_values(values)

    with open('{0}_MA{1}'.format(*splitext(data_csv_path)), 'w+') as destination:
        fieldnames = ['Sample', 'Label'] + standardized_compound_names
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(cleaned_values)):
            rowdict = {field: value for field, value in zip(
            fieldnames, [sample_names[i], str(sample_labels[i])] + cleaned_values[i])}
            writer.writerow(rowdict)

def consolidate_sample_metadata(sample_metadata, label_info_entry_idx, litter_info_entry_idx):
    """
    Infer good sample names from sample metadata entries
    :param sample_metadata: A 2-D list. Each row is a list of metadata fields for each sample.
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
    fieldnames = [strip_suffix(x) for x in original_fieldnames]
    return [name_map[field] if field.lower() in name_map else field for field in fieldnames]

def strip_suffix(name):
    stripped = name
    suffixes = ['-nega', '-posi', 'nega', 'posi']
    for s in suffixes:
        if name.endswith(s):
            stripped = name[:-len(s)]
            break
    return stripped

def clean_values(values):
    """
    Clean values found in dataset.
    :param values: 2D array of data values. Example: [1, 'N/A', '2], [3, 4, 5]
    :return: 2D array of cleaned data values. Example: [1, '', 2], [3, 4, 5]
    """
    unwanted_values = ['N/A', 'Unknown', 'NaN']
    return [['' if x in unwanted_values else x for x in row] for row in values]
