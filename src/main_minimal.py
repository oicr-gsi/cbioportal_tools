# Command Line Imports
import argparse
# Other Scripts
import generate_study_meta
import generate_data_meta_samples
import helper


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")

    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-i", "--study-input-folder",
                          type=lambda folder: helper.check_files_in_folder(helper.extensionChoices, folder, parser),
                          help="The input folder can contain compressed: [" +
                               " | ".join(helper.compressedChoices) + "] "
                                                                      " or uncompressed format in: [" +
                               " | ".join(helper.extensionChoices) + "] ",
                          metavar='')
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
                             "indicated in the help if you use this")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    # Still need to collect the name and the description
    return parser


def gen_study_meta(args, verb):
    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(args.study_folder)
    helper.working_on(args.verbose)

    helper.working_on(verb, message='Saving meta_study.txt ...')
    generate_study_meta.save_meta_cancer_study(args)
    helper.working_on(args.verbose)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(args.verbose, message='Success! The cancer study meta has been saved!')


def gen_samples_meta_data(args, verb):
    helper.working_on(verb, message='Gathering patient and sample IDs...')
    patient_sample_ids = generate_data_meta_samples.gather_patient_and_sample_ids(args.study_input_folder)
    helper.working_on(verb)

    # TODO:: More information should be added to the patient_sample_ids
    # Think about adding attributes like add_cancer_subtype(patient_sample_ids)

    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(args.study_output_folder)
    helper.working_on(args.verbose)

    helper.working_on(verb, message='Saving data_clinical_samples.txt ...')
    generate_data_meta_samples.save_data_samples(patient_sample_ids)
    helper.working_on(verb)

    helper.working_on(verb, message='Saving meta_clinical_samples.txt ...')
    generate_data_meta_samples.save_sample_meta_file(args.study_id)
    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The cancer samples meta and data has been saved!')


def main():
    args = define_parser().parse_args()
    verb = args.verbose

    gen_study_meta(args, verb)
    gen_samples_meta_data(args, verb)
    helper.working_on(verb, message='A minimal study should now be complete!')


if __name__ == '__main__':
    main()
