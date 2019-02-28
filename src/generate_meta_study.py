__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import argparse


meta_study = 'meta_study.txt'


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
    required.add_argument("-c", "--cli-study",
                          help="Command Line Input, the description, name, short_name and type_of_cancer in semi-colon "
                               "separated values. Input needs to be wrapped with ''."
                               "e.g. -c 'GECCO Samples sequenced and analyzed at OICR;Genetics and "
                               "Epidemiology of Colorectal Cancer Consortium;GECCO;colorectal'",
                          metavar='STRING')
    parser.add_argument("-d", "--default",
                        action="store_true",
                        help="Prevents need for user input by trying to parse study ID, you must follow format "
                             "indicated in the help if you use this. **This tag is not recommended and cannot be used "
                             "alongside -c. If you do -c takes precedence.")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    return parser


def save_meta_cancer_study(args):
    study_id = args.study_id
    if args.cli_study:
        [description, name, short_name, type_of_cancer] = args.cli_study.split(';')
    elif args.default:
        # Else attempt to make the best description with limited information
        split = study_id.split('_')
        type_of_cancer = split[0]
        description = 'Cancer study on {} by {} conducted in {}.'.format(*split)
        split[0] = split[0].upper()
        split[1] = split[1].upper()
        name = '{} {} ({})'.format(*split)
        short_name = '{} ({})'.format(*split)
    else:
        raise AttributeError("ERROR: Neither --cli-study, nor --default were specified. "
                             + "Please try again specifying either!")
    # Write information to file
    f = open(meta_study, 'w+')
    f.write('type_of_cancer: ' + type_of_cancer + '\n')
    f.write('cancer_study_identifier: ' + study_id + '\n')
    f.write('name: ' + name + '\n')
    f.write('description: ' + description + '\n')
    f.write('short_name: ' + short_name + '\n')
    f.write('add_global_case_list: true\r')
    f.close()


if __name__ == '__main__':
    # Other Scripts
    import COWtown
    args = define_parser().parse_args()
    verb = args.verbose
    COWtown.gen_study_meta(args, verb)
