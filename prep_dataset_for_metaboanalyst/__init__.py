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

def prep_dataset(data_csv, num_id_entries, label_info_entry_idx, litter_info_entry_idx):
    with open(data_csv) as source:
        with open('{0}_{1}'.format('metaboanalyst', data_csv)) as destination:
            reader = csv.DictReader(source)

            # Grab the sample metadata entries from the source file
            sample_metadata = []
            for i in range(num_id_entries):
                sample_metadata.append(source.readline())

            sample_names, sample_labels = consolidate_sample_metadata(sample_metadata, label_info_entry_idx, litter_info_entry_idx)

            # Standardize compound names using the name map
            standardized_compound_names = standardize_compound_names(reader.fieldnames[num_id_entries:])
            standardized_compound_names = [''].extend(standardized_compound_names)
            writer = csv.DictWriter(destination, fieldnames=standardized_compound_names)
            writer.writeheader()
            writer.writerow(['Sample'].extend(sample_names))
            writer.writerow(['Label'].extend(sample_labels))


def consolidate_sample_metadata(sample_metadata, label_info_entry_idx, litter_info_entry_idx):
    # Infer good sample names from sample metadata entries
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
        sample_ids.append('_'.join[str(i), label, litter])
        sample_labels.append(label_numbers['label'])
    return sample_ids, sample_labels

def infer_label(label_entry):
    possible_labels = []
    label_entry_l = label_entry.tolower
    for label in label_map:
        is_label = any(map(lambda x: label_entry_l.contains(x), label_map[label]))
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

def standardize_compound_names(original_fieldnames):
    name_map = NameMap()
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