# Command Line Imports
import argparse
import os

# Data Processing Imports
import pandas as pd
import random

# Other Scripts
import main_minimal

meta_cancer_type = 'meta_cancer_type.txt'
data_cancer_type = 'data_cancer_type.txt'
meta_study = 'meta_study.txt'


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")

    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-c", "--cli-study",
                          help="Command Line Input, the description, name, short_name and type_of_cancer in semi-colon "
                               "separated values. Input needs to be wrapped with ''."
                               "e.g. -c 'GECCO Samples sequenced and analyzed at OICR;Genetics and "
                               "Epidemiology of Colorectal Cancer Consortium;GECCO;colorectal'",
                          metavar='STRING')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Forces overwriting of data_cancer_type.txt file.")
    return parser


def get_colours():
    return pd.read_csv('colours.txt', delimiter='|', header=None)


def gen_cancer_type_meta():
    f = open(meta_cancer_type, 'w+')
    f.write('genetic_alteration_type: CANCER_TYPE\n')
    f.write('datatype: CANCER_TYPE\n')
    f.write('data_filename: {}\n'.format(data_cancer_type))


def write_data_meta_cancer_type(colours, type_of_cancer):
    name = type_of_cancer.capitalize()
    clinical_trial_keywords = [type_of_cancer, name]
    colour = colours.iloc[random.randint(0, len(colours))][0]
    parent_type_of_cancer = 'tissue'
    f = open(data_cancer_type, 'w+')
    f.write('{}\t{}\t{}\t{}\t{}\r'.format(type_of_cancer,
                                          name,
                                          ','.join(clinical_trial_keywords),
                                          colour,
                                          parent_type_of_cancer))
    f.close()


def create_file(args, colours):
    type_of_cancer = args.cli_study.split(';')[3]
    write_data_meta_cancer_type(colours, type_of_cancer)


def gen_cancer_type_data(args, colours):
    if args.force:
        create_file(args, colours)
    else:
        try:
            os.stat(data_cancer_type)
            print '{} already exists, if you want to regenerate it please remove it using'.format(data_cancer_type)
            print 'rm {}'.format(data_cancer_type)
            print 'or use the -f / --force tag'
        except OSError:
            create_file(args, colours)


if __name__ == '__main__':
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_cancer_type_meta_data(args, verb)
