import argparse
import os

import pandas
import numpy as np

extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]


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

    parser.add_argument("-s", "--study_folder",
                        help="The folder you want to export this generated data_samples.txt file to. Generally this "
                             "will be the main folder of the study being generated. If left blank this will generate it"
                             " wherever you run the script from.",
                        metavar='')

    return parser


def gather_patient_and_sample_ids(parser):
    # List all files in folder, remove extensions and generate patient and sample IDs
    folder = os.listdir(parser.parse_args().input_folder)
    key_val = []
    for each in folder:
        # Strips each of the exts from the string
        exts = ['.gz', '.tar', '.vcf', '.maf']
        for every in exts:
            remove_end_string(each, every)

        split = each.split("_")
        patient_id = []
        # Generate Patient ID from file name of the form "string_number"
        for every in split:
            try:
                patient_id += every + '_'
                int(every)
                break
            except ValueError:  # Catch and do nothing
                continue
        patient_id = ''.join(patient_id[:-1])
        key_val += [patient_id, each]
    key_val = np.reshape(key_val, (len(key_val) / 2, 2))
    return key_val


def change_folder(folder):
    try:
        os.chdir(folder)
    except OSError:
        for a in range(30):
            print('*')
        print 'The path to your folder probably does not exist. Trying to make the folder for you.'
        for a in range(30):
            print('*')
        try:
            os.mkdir(folder)
        except OSError:
            raise ValueError('You may not have permission to create folders there. Very sad')


def save_dataframe(dataset):
    # If we are in destination folder, export the data_samples.txt that we have generated.
    dataset.to_csv('data_clinical_samples.txt', sep='\t')


def save_sample_metafile(id):
    # Generating the meta file is almost as important
    f = open('meta_clinical_sample.txt', 'w+')
    f.write('cancer_study_identifier: ' + id)
    f.write('genetic_alteration_type: CLINICAL')
    f.write('datatype: SAMPLE_ATTRIBUTES')
    f.write('data_filename: data_clinical_patient.txt')
    f.close()


def main():
    # Regular main method
    parser = define_parser()
    study_folder = parser.parse_args().study_folder
    study_id = parser.parse_args().study_id
    patient_sample_ids = gather_patient_and_sample_ids(parser)
    # This is where more information would be added to the patient_sample_ids
    # Ex. add_cancer_subtype(patient_sample_ids)
    # I would also consider renaming the variable to dataset
    change_folder(study_folder)
    save_dataframe(patient_sample_ids)
    save_sample_metafile(study_id)


if __name__ == '__main__':
    main()
