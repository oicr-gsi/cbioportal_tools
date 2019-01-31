# Command Line Imports
import argparse
import os

# Data Processing Imports
import pandas as pd
import random

# Other Scripts
import main_minimal


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    return parser


def get_colours():
    return pd.read_csv('colours.txt', delimiter='|', header=None)


def gen_cancer_type_meta():
    f = open('meta_cancer_type.txt', 'w+')
    f.write('genetic_alteration_type: CANCER_TYPE\n')
    f.write('datatype: CANCER_TYPE\n')
    f.write('data_filename: data_cancer_type.txt\n')


def gen_cancer_type_data(colours):
    try:
        os.stat('data_cancer_type.txt')
        print 'data_cancer_type.txt already exists, if you want to regenerate it please remove it using'
        print 'rm data_cancer_type.txt'
    except OSError:
        print 'There is no pre-existing meta_cancer_type.txt; attempting to generate one now...'
        try:
            os.stat('meta_study.txt')
            f = open('meta_study.txt', 'r+')
            type_of_cancer = f.readline().split(':')[1].strip()
        except:
            print('Could not find study_meta has it been deleted?')
            print("Write the type_of_cancer of the cancer e.g. 'colorectal': \n")
            type_of_cancer = raw_input()
        name = type_of_cancer.capitalize()
        clinical_trial_keywords = [type_of_cancer, name]
        colour = colours.iloc[random.randint(0, len(colours))][0]
        parent_type_of_cancer = 'tissue'
        f = open('data_cancer_type.txt', 'w+')
        f.write('{}\t{}\t{}\t{}\t{}'.format(type_of_cancer,
                                            name,
                                            ','.join(clinical_trial_keywords),
                                            colour,
                                            parent_type_of_cancer)
                )
        f.close()


if __name__ == '__main__':
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_cancer_type_meta_data(args, verb)
