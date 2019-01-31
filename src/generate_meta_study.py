# Command Line Imports
import argparse
# Other Scripts
import main_minimal


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
                          metavar='')
    required.add_argument("-o", "--study-output-folder",
                          help="The folder you want to export this generated data_samples.txt file to. Generally this "
                               "will be the main folder of the study being generated. If left blank this will generate "
                               "it wherever you run the script from.",
                          metavar='',
                          default='.')
    parser.add_argument("-d", "--default",
                        action="store_true",
                        help="Prevents need for user input by trying to parse study ID, you must follow format "
                             "indicated in the help if you use this. **This tag is not recommended and cannot be used "
                             "alongside -c. If you do -c takes precedence.")
    parser.add_argument("-c", "--cli",
                        help="Command Line Input, the description, name, short_name and type_of_cancer in semi-colon "
                             "separated values. Input needs to be wrapped with ''."
                             "e.g. -c 'GECCO Samples sequenced and analyzed at OICR;Genetics and "
                             "Epidemiology of Colorectal Cancer Consortium;GECCO;colorectal'",
                        metavar='')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    return parser


def save_meta_cancer_study(args):
    study_id = args.study_id
    if args.cli:
        [description, name, short_name, type_of_cancer] = args.cli.split(';')
    elif args.default:
        # Else attempt to make the best description with limited information
        split = study_id.split('_')
        type_of_cancer = split[0]
        description = 'Cancer study on {} by {} conducted in {}.'.format(*split)
        split[0] = split[0].upper()
        split[1] = split[1].upper()
        name = '{} {} ({})'.format(*split)
        short_name = '{} ({})'.format(*split)
    # Write information to file
    f = open('meta_study.txt', 'w+')
    f.write('type_of_cancer: ' + type_of_cancer + '\n')
    f.write('cancer_study_identifier: ' + study_id + '\n')
    f.write('name: ' + name + '\n')
    f.write('description: ' + description + '\n')
    f.write('short_name: ' + short_name + '\n')
    f.close()


if __name__ == '__main__':
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_study_meta(args, verb)
