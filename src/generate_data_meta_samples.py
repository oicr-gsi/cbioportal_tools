import argparse
import os

import pandas as pd
import numpy as np

import re
import helper

extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]
verbosity = False


def check_files_in_folder(choices, folder, parser):
    # Checks file extensions within folder for belonging in extensionChoices (important constants)
    for each in os.listdir(folder):
        ext = each.split('.')
        if not (bool(set(ext) & set(choices))):
            parser.error(each + " file doesn't end with one of {}".format(choices))
    return folder


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")

    parser.add_argument("input_folder",
                        type=lambda folder: check_files_in_folder(extensionChoices, folder, parser),
                        help="The input folder can contain compressed: [" +
                             " | ".join(compressedChoices) + "] "
                             " or uncompressed format in: [" +
                             " | ".join(extensionChoices) + "] ")

    parser.add_argument("-i", "--study-id",
                        help="This is the cancer study ID, a unique string. This will soon be managed another way",
                        metavar='')

    parser.add_argument("-s", "--study-folder",
                        help="The folder you want to export this generated data_samples.txt file to. Generally this "
                             "will be the main folder of the study being generated. If left blank this will generate it"
                             " wherever you run the script from.",
                        metavar='')

    parser.add_argument("-v", "--verbose",
                        action= "store_true",
                        help="Makes program verbose")

    return parser


def gather_patient_and_sample_ids(args):
    # List all files in folder and generate patient and sample IDs
    folder = os.listdir(args.input_folder)
    key_val = []
    # This regular expression is very specific to GECCO
    # Make Regular Expression for: GECCO_1111_Xx_Y or something similar
    regex = re.compile('[A-Z]{5}_[0-9]{4}_[a-zA-Z]{2}_[A-Z]')
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
    print data_set
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


def main():
    # Regular main method
    args = define_parser().parse_args()
    global verbosity
    verbosity = args.verbose

    helper.working_on(verbosity, message='parsing arguments...')
    study_folder = args.study_folder
    study_id = args.study_id
    helper.working_on(verbosity)

    helper.working_on(verbosity, message='Gathering patient and sample IDs...')
    patient_sample_ids = gather_patient_and_sample_ids(args)
    helper.working_on(verbosity)

    # This is where more information would be added to the patient_sample_ids
    # Ex. add_cancer_subtype(patient_sample_ids)
    # I would also consider renaming the variable to dataset

    helper.working_on(verbosity, message='Saving gathered information...')
    original_dir = helper.change_folder(study_folder)
    save_data_samples(patient_sample_ids)
    save_sample_meta_file(study_id)
    helper.working_on(verbosity)

    helper.reset_folder(original_dir)
    helper.working_on(verbosity, message='generating_bare_data_samples.py has successfully completed!')
    helper.working_on(verbosity)


if __name__ == '__main__':
    main()
