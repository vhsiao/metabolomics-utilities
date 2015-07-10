__author__ = 'vhsiao'

import csv
from os.path import splitext, dirname
import sys
sys.path.extend([dirname(dirname(__file__))])

from name_map_utils import NameMap, default_map_pkl_path
from name_map_utils import standard_name, pubchem, hmdb, kegg

label_map = {
    'wt': ['wt', 'wild'],  # wild type
    'he': ['het', 'he'],  # heterozygote
    'ho': ['hom', 'mut', 'ho']  # homozygote
}

label_numbers = {'wt': 1, 'he': 2, 'ho': 3, 'unknown': 99}


def prep_dataset(data_csv_path, num_metadata_fields, label_info_field_idx, data_organized_in='cols',
                 litter_info_field_idx=None, map_pkl_path=default_map_pkl_path, resolve_names=True,
                 id_type=standard_name):
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

        raw_metadata = [row[1:] for row in dataset[:num_metadata_fields]]
        if label_info_field_idx is not None:
            # Grab the sample metadata entries from the source file. Discard the first column ('Sample Name', etc).
            metadata_keys = ['Sample', 'Label']
            metadata = consolidate_sample_metadata(raw_metadata, label_info_field_idx, litter_info_field_idx)
        else:
            # Copy the metadata rows as they are.
            metadata_keys = [row[0] for row in dataset[:num_metadata_fields]]
            metadata = raw_metadata

        # Standardize compound names using the name map
        compound_names = [row[0] for row in dataset[num_metadata_fields:]]
        if resolve_names:
            resolved = standardized_compound_names(compound_names, map_pkl_path=map_pkl_path, id_type=id_type)
        else:
            resolved = compound_names

        # Clean up the data values
        values = zip(*[row[1:] for row in dataset[num_metadata_fields:]])
        cleaned_values = clean_values(values)

    dest_path = '{0}_MA{1}'.format(*splitext(data_csv_path))
    with open(dest_path, 'w+') as destination:
        fieldnames = metadata_keys + resolved
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(cleaned_values)):
            rowdict = {field: value for field, value in zip(
                fieldnames, [str(metadata_entry[i]) for metadata_entry in metadata] + cleaned_values[i])}
            writer.writerow(rowdict)

def consolidate_sample_metadata(sample_metadata, label_info_entry_idx, litter_info_entry_idx=None):
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

    # Litter information if available
    litter_info = None
    if litter_info_entry_idx:
        try:
            litter_info = sample_metadata[litter_info_entry_idx]
        except IndexError:
            print "Invalid litter info entry. Litter info will not be included in the sample id."
        except:
            raise

    sample_ids = []
    sample_labels = []
    for i in range(len(label_info)):
        label = infer_label(label_info[i])
        litter = ''
        if litter_info:
            litter = 'L' + ''.join([c for c in litter_info[i] if c.isdigit()])
        sample_id = '_'.join([str(i), label, litter])
        sample_ids.append(sample_id)
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

def standardized_compound_names(original_names, map_pkl_path=default_map_pkl_path, id_type=standard_name):
    """
    :param original_names: A list of original field names to be standardized
    :param map_pkl_path: Path to a pkl file containing mappings used to standardize the names
    :return: A list of standardized field names
    """
    print 'Standardizing names to: {0}'.format(id_type)
    name_map = NameMap(map_pkl_path)
    standardized = original_names
    for i in range(len(standardized)):
        name = _strip_suffix(standardized[i])
        if name in name_map:
            new_id = name_map[name][id_type] if id_type in name_map[name] else name
            print '{0} --> {1}'.format(standardized[i], new_id)
            standardized[i] = new_id
        else:
            standardized[i] = name
    return standardized

def clean_values(values):
    """
    Clean values found in dataset.
    :param values: 2D array of data values. Example: [1, 'N/A', '2], [3, 4, 5]
    :return: 2D array of cleaned data values. Example: [1, '', 2], [3, 4, 5]
    """
    unwanted_values = ['N/A', 'Unknown', 'NaN', 'NA']
    return [['' if x in unwanted_values else x for x in row] for row in values]

def _strip_suffix(name):
    stripped = name
    suffixes = ['-nega', '-posi', 'nega', 'posi']
    for s in suffixes:
        if name.endswith(s):
            stripped = name[:-len(s)]
            print '  {name} --> {stripped}'.format(name=name, stripped=stripped)
            break
    return stripped
