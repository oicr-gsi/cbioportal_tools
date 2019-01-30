# Command Line Imports
import argparse
import os
# Data Processing Imports
import pandas as pd
import numpy as np

import re
# Other Scripts
import helper
import main_minimal


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")
    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-f", "--study-input-folder",
                          type=lambda folder: helper.check_files_in_folder(helper.extensionChoices, folder, parser),
                          help="The input folder can contain compressed: [" +
                               " | ".join(helper.compressedChoices) + "] "
                                                                      " or uncompressed format in: [" +
                               " | ".join(helper.extensionChoices) + "] ",
                          metavar='')
    required.add_argument("-i", "--study-id",
                          help="This is the cancer study ID, a unique string. Please use the format gene_lab_year. e.g."
                               "brca_gsi_2019 or mixed_tgl_2020",
                          metavar='')
    required.add_argument("-s", "--study-folder",
                          help="The folder you want to export this generated data_samples.txt file to. Generally this "
                               "will be the main folder of the study being generated. If left blank this will generate "
                               "it wherever you run the script from.",
                          metavar='',
                          default='.')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")

    return parser


def gather_patient_and_sample_ids(input_folder):
    # List all files in folder
    folder = os.listdir(input_folder)
    key_val = []
    # This regular expression is very specific to GECCO
    # Make Regular Expression for: GECCO_1111_Xx_Y or something similar
    regex = re.compile('[A-Z]{5}_[0-9]{4}_[a-zA-Z]{2}_[A-Z]')
    # Generate patient and sample IDs
    for each in folder:
        try:
            # Check if the file match the pattern
            start, end = regex.search(each).span()
            patient_id = each[start:start+10]
            sample_id = each[start:end]
        except AttributeError:
            # As of now, throw an error.
            # Later we can consider changing this to skip erroneous files
            raise ValueError('You have a possibly erroneous file in the folder please remove it or something?\n' + each)
        key_val += [[patient_id, sample_id]]
    key_val = np.reshape(key_val, (len(key_val), 2))
    # Convert list to np.array
    return key_val


def save_data_samples(data_set):
    # We are in destination folder, export the data_samples.txt that we have generated.
    new_data_set = pd.DataFrame({'PATIENT_ID': data_set[:, 0], 'SAMPLE_ID': data_set[:, 1]})
    new_data_set.to_csv('data_clinical_samples.txt', sep='\t', index=False)


def save_sample_meta_file(study_id):
    # Generating the meta file is almost as important
    f = open('meta_clinical_sample.txt', 'w+')
    f.write('cancer_study_identifier: ' + study_id + '\n')
    f.write('genetic_alteration_type: CLINICAL\n')
    f.write('datatype: SAMPLE_ATTRIBUTES\n')
    f.write('data_filename: data_clinical_patient.txt\n')
    f.close()


if __name__ == '__main__':
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_samples_meta_data(args, verb)
