# Command Line Imports
import argparse
import os

# Data Processing Imports
import pandas as pd

# Other Scripts
import helper
import main_minimal

case_folder = 'case_lists/'
cases_txt = 'cases_all.txt'


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")
    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-s", "--study-id",
                          help="This is the cancer study ID, a unique string. Please use the format gene_lab_year. e.g."
                               "brca_gsi_2019 or mixed_tgl_2020",
                          metavar='STRING')
    required.add_argument("-i", "--study-input-folder",
                          type=lambda folder: helper.check_files_in_folder(helper.extensionChoices, folder, parser),
                          help="The input folder can contain compressed: [" +
                               " | ".join(helper.compressedChoices) + "] "
                                                                      " or uncompressed format in: [" +
                               " | ".join(helper.extensionChoices) + "] ",
                          default='.',
                          metavar='FOLDER')
    required.add_argument("-l", "--cli-case-list",
                          help="Command Line Input, case_list_name and case_list_description in semi-colon "
                               "separated values. Input needs to be wrapped with ''."
                               "e.g. -c 'All Tumours;All tumor samples (over 9000 samples)'",
                          metavar='STRING')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    return parser


def test_case_lists_folder():
    try:
        os.stat(case_folder)
    except OSError:
        os.mkdir(case_folder)


def save_meta_case_lists(patient_sample_ids, args):
    samples = patient_sample_ids[:, 1]
    stable_id = args.study_id + '_custom'
    [case_list_name, case_list_description] = args.cli_case_list.split(';')

    f = open(cases_txt, 'w+')
    f.write('cancer_study_identifier: {}\n'.format(args.study_id))
    f.write('stable_id: {}\n'.format(stable_id))
    f.write('case_list_name: {}\n'.format(case_list_name))
    f.write('case_list_description: {}\n'.format(case_list_description))
    f.write('case_list_ids: ' + '\t'.join(samples))
    f.close()


if __name__ == '__main__':
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_cancer_list_meta(args, verb)
