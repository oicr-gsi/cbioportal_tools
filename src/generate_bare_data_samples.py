import argparse
import os

import pandas as pd
import numpy as np

import re

extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]
verbosity = False


def remove_end_string(string, remove):
    string = str(string)
    if string.endswith(remove):
        string = string[:-len(remove)]
    return string


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
    # List all files in folder, remove extensions and generate patient and sample IDs
    folder = os.listdir(args.input_folder)
    key_val = []
    regex = re.compile('[A-Z]{5}_[0-9]{4}_[a-zA-Z]{2}_[A-Z]')
    for each in folder:
        # Make Regular Expression for: GECCO_1111_Xx_Y or something similar
        try:
            start, end = regex.search(each).span()
            patient_id = each[start:start+10]
            sample_id = each[start:end]
        except AttributeError:
            raise ValueError('You have a possibly erroneous file in the folder please remove it or something?\n' + each)
        key_val += [patient_id, sample_id]
    key_val = np.reshape(key_val, (len(key_val) / 2, 2))
    return key_val


def change_folder(folder):
    original_working_directory = os.getcwd()
    try:
        os.chdir(folder)
    except OSError:
        for a in range(30):
            print('*',)
        print 'The path to your folder probably does not exist. Trying to make the folder for you.'
        for a in range(30):
            print('*',)
        try:
            os.mkdir(folder)
        except OSError:
            raise ValueError('You may not have permission to create folders there. Very sad')
    return original_working_directory


def success():
    print 'Success!'


def working_on(message):
    if verbosity:
        print message


def reset_folder(owd):
    os.chdir(owd)


def save_dataframe(dataset):
    # We are in destination folder, export the data_samples.txt that we have generated.
    print dataset
    new_dataset = pd.DataFrame({'PATIENT_ID': dataset[:, 0], 'SAMPLE_ID': dataset[:, 1]})
    new_dataset.to_csv('data_clinical_samples.txt', sep='\t', index=False)


def save_sample_metafile(id):
    # Generating the meta file is almost as important
    f = open('meta_clinical_sample.txt', 'w+')
    f.write('cancer_study_identifier: ' + id + '\n')
    f.write('genetic_alteration_type: CLINICAL\n')
    f.write('datatype: SAMPLE_ATTRIBUTES\n')
    f.write('data_filename: data_clinical_patient.txt\n')
    f.close()


def main():
    # Regular main method
    args = define_parser().parse_args()
    global verbosity
    verbosity = args.verbose

    working_on('parsing arguments...')
    study_folder = args.study_folder
    study_id = args.study_id
    success()

    working_on('Gathering patient and sample IDs...')
    patient_sample_ids = gather_patient_and_sample_ids(args)
    success()

    # This is where more information would be added to the patient_sample_ids
    # Ex. add_cancer_subtype(patient_sample_ids)
    # I would also consider renaming the variable to dataset

    working_on('Saving gathered information...')
    original_dir = change_folder(study_folder)
    save_dataframe(patient_sample_ids)
    save_sample_metafile(study_id)
    success()

    reset_folder(original_dir)
    working_on('generating_bare_data_samples.py has successfully completed!')


if __name__ == '__main__':
    main()
