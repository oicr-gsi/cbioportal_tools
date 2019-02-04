import os

import numpy as np
import re


extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]


def stars():
    # Prints a row of stars
    for a in range(30):
        print('*'),
    print('')


def change_folder(folder):
    # Try to safely change working directory
    original_working_directory = os.getcwd()
    try:
        os.chdir(folder)
    except OSError:
        stars()
        print('The path to your folder probably does not exist. Trying to make the folder for you.')
        stars()
        try:
            os.mkdir(folder)
            os.chdir(folder)
        except OSError:
            stars()
            raise ValueError('You may not have permission to create folders there. Very sad')
    return original_working_directory


def reset_folder(owd):
    os.chdir(owd)
    # Go to original working directory, needs to be used in junction to stored variable


def working_on(verbosity, message='Success!'):
    # Method is for verbose option. Prints Success if no parameter specified
    if verbosity:
        print(message)


def check_files_in_folder(choices, folder, parser):
    # Checks file extensions within folder for belonging in extensionChoices (important constants)
    for each in os.listdir(folder):
        ext = each.split('.')
        if not (bool(set(ext) & set(choices))):
            parser.error(each + " file doesn't end with one of {}".format(choices))
    return folder


def write_tsv_dataframe(name, dataset):
    dataset.to_csv(name, sep='\t', index=False)


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
            raise ValueError('ERROR: You have a possibly erroneous file in the folder please remove it or something?\n'
                             + each)
        key_val += [[patient_id, sample_id]]
    key_val = np.reshape(key_val, (len(key_val), 2))
    # Convert list to np.array
    return key_val
