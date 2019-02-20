__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import argparse
import subprocess
import os

import pandas as pd

# Other Scripts
import generate_meta_case_list
import generate_data_meta_samples
import generate_data_meta_cancer_type
import generate_data_meta_mutation_data
import helper
import Config

meta_info_map = {'mutation':   ['MUTATION_EXTENDED', 'MAF', '_sequenced', 'true'],
                 'sample':     ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 'patient':    ['CLINICAL', 'PATIENT_ATTRIBUTES']}

# TODO:: Add all the other data types.
# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4


global_zip =    ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']

case_list_map = {'mutation': '_sequenced',
                 'dCNA': '_cna'}
# dCNA => discrete Copy Number Variation


def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")

    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-o", "--study-output-folder",
                          type=lambda folder: os.path.abspath(folder),
                          help="The main folder of the study you want to generate.",
                          metavar='FOLDER',
                          default='new_study/')
    required.add_argument("-s", "--study-info",
                          help="The location of the study input information",
                          metavar='FILE')
    parser.add_argument("-p", "--push",
                        action="store_true",
                        help="Push the generated study to the cBioPortal Instance")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Forces overwriting of data_cancer_type.txt file and *.maf files.")
    return parser


def get_config(file, f_type, verb):
    f = open(file, 'r')

    helper.working_on(verb, message='Reading information')
    file_map = {}
    for line in f:
        if line[0] == '#':
            line = line.strip().replace('#', '').split('=')
            file_map[line[0]] = line[1]
        else:
            break
    data_frame = pd.read_csv(file, delimiter='\t', skiprows=len(file_map), dtype=object)
    config_file = Config.Config(file_map, data_frame, f_type)
    return config_file


def generate_meta_file(meta_config: Config.Config, study_config: Config.Config, verb):
    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(study_config.config_map['study_output_folder'])
    helper.working_on(verb)

    # TODO:: Add functionality for optional fields

    helper.working_on(verb, message='Saving meta_{}.txt ...'.format(meta_config.type_config))
    f_out = 'meta_{}.txt'.format(meta_config.type_config)
    f = open(f_out, 'w')
    if not meta_config.type_config == 'cancer_type':
        # Cancer_type meta file is the only one not to contain the identifier with the meta-data
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))

    if not meta_config.type_config == 'expression':
        for field, entry in zip(global_zip, meta_info_map[meta_config.type_config]):
            f.write('{}: {}\n'.format(field, entry))
    else:
        for field, entry in zip(global_zip[:3] + ['source_stable_id'] + global_zip[3:],
                                meta_info_map[meta_config.type_config]):
            f.write('{}: {}\n'.format(field, entry))

    if 'profile_name' in meta_config.config_map and 'profile_description' in meta_config.config_map:
        f.write('profile_name: {}\n'.format(meta_config.config_map['profile_name']))
        f.write('profile_description: {}\n'.format(meta_config.config_map['profile_description']))

    f.write('data_filename: data_{}.txt\n'.format(meta_config.type_config))
    f.flush()
    os.fsync(f)
    f.close()
    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The {} meta has been saved!'.format(meta_config.type_config))


def generate_meta_study(study_config: Config.Config, verb):
    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(study_config.config_map['study_output_folder'])
    helper.working_on(verb)

    helper.working_on(verb, message='Saving meta_study.txt ...')

    f = open('meta_study.txt', 'w')

    f.write('type_of_cancer: {}\n'.format(study_config.config_map['type_of_cancer']))
    f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
    f.write('name: {}\n'.format(study_config.config_map['name']))
    f.write('short_name: {}\n'.format(study_config.config_map['short_name']))
    f.write('description: {}\n'.format(study_config.config_map['description']))
    f.write('add_global_case_list: true\r')
    f.flush()
    os.fsync(f)
    f.close()

    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The cancer study meta has been saved!')


def generate_data_file(meta_config: Config.Config, study_config: Config.Config, force, verb):

    if meta_config.type_config == 'mutation':
        helper.working_on(verb, message='Gathering and decompressing files into temporary folder...')
        generate_data_meta_mutation_data.decompress_to_temp(meta_config)
        helper.working_on(verb)

        helper.working_on(verb, message='Exporting vcf2maf...')
        helper.working_on(verb, message='And deleting .vcf s...')
        generate_data_meta_mutation_data.export2maf(meta_config, force, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Concatenating .maf files...')
        generate_data_meta_mutation_data.concat_files_maf(meta_config, study_config)
        helper.working_on(verb)


def generate_case_list(meta_config: Config.Config, study_config: Config.Config):
    if meta_config.type_config in case_list_map.keys():
        case_list_folder = os.path.join(study_config.config_map['output_folder'], 'case_lists')
        if not os.path.exists(case_list_folder):
            os.makedirs(case_list_folder)

        f = open('{}/{}'.format(case_list_folder, case_list_map[meta_config.type_config]), 'w')
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'],
                                           case_list_map[meta_config.type_config]))
        f.write('case_list_name: {}\n'.format(meta_config.config_map['profile_name']))
        f.write('case_list_description: {}\n'.format(meta_config.config_map['profile_description']))
        f.write('case_list_ids: {}\n'.format('\t'.join(meta_config.data_frame['Patient_ID'])))
        f.flush()
        os.fsync(f)
        f.close()



def gen_samples_meta_data(args, verb, conv_info):
    # TODO:: Port to new format
    helper.working_on(verb, message='Changing folder to temp...')
    original_dir = helper.change_folder(helper.get_temp_folder(args, 'vcf'))
    helper.working_on(verb)

    helper.working_on(verb, message='Changing folder to output...')
    helper.reset_folder(original_dir)
    original_dir = helper.change_folder(args.study_output_folder)
    helper.working_on(verb)

    helper.working_on(verb, message='Saving data_clinical_samples.txt ...')
    generate_data_meta_samples.save_data_samples(conv_info)
    helper.working_on(verb)

    helper.working_on(verb, message='Saving meta_clinical_samples.txt ...')
    generate_data_meta_samples.save_meta_samples(args.study_id)
    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The cancer samples meta and data has been saved!')


def gen_cancer_type_meta_data(args, verb):
    # TODO:: Port to new format
    helper.working_on(verb, message='Reading colours...')
    colours = generate_data_meta_cancer_type.get_colours()
    helper.working_on(verb)

    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(args.study_output_folder)
    helper.working_on(verb)

    helper.working_on(verb, message='Generating cancer_type records...')
    generate_data_meta_cancer_type.gen_cancer_type_data(args, colours)
    helper.working_on(verb)

    helper.working_on(verb, message='Generating cancer_type meta...')
    generate_data_meta_cancer_type.gen_cancer_type_meta()
    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The cancer study meta has been saved!')


def gen_case_list_meta(args, verb, conv_info):
    # TODO:: Port to new format
    helper.working_on(verb, message='Changing folder to temp...')
    original_dir = helper.change_folder(helper.get_temp_folder(args, 'vcf'))
    helper.working_on(verb)

    helper.working_on(verb, message='Jumping into Study Output Folder...')
    helper.change_folder(args.study_output_folder)
    helper.working_on(verb)

    helper.working_on(verb, message='Testing Case_Lists Folder...')
    generate_meta_case_list.test_case_lists_folder()
    helper.working_on(verb)

    helper.working_on(verb, message='Jumping into Case_Lists Folder...')
    helper.change_folder(generate_meta_case_list.case_folder)
    helper.working_on(verb)

    helper.working_on(verb, message='Saving Meta Case List...')
    generate_meta_case_list.save_meta_case_lists(conv_info, args)
    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The cancer case lists has been saved!')


def export_study_to_cbioportal(args, verb):
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Copying folder to cBioPortal instance at 10.30.133.80 ...')

    # Cleanup Location
    subprocess.call("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                    "rm -r ~/oicr_studies/{}; "
                    "mkdir ~/oicr_studies/{}'".format(args.cbioportal_key,
                                                      os.path.basename(args.study_output_folder),
                                                      os.path.basename(args.study_output_folder)
                                                      ),
                    shell=True)
    # Copy over
    subprocess.call('scp -r -i {} {} debian@10.30.133.80:/home/debian/oicr_studies'.format(args.cbioportal_key,
                                                                                           args.study_output_folder),
                    shell=True)
    helper.working_on(verb)
    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')
    subprocess.call("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                    "./metaImport.py -s ~/oicr_studies/{} "
                    "-u http://10.30.133.80:8080/cbioportal "
                    "-o'".format(args.cbioportal_key,
                                 os.path.basename(args.study_output_folder),
                                 os.path.basename(args.study_output_folder),
                                 os.path.basename(args.study_output_folder)
                                 ),
                    shell=True)
    subprocess.call("ssh -i {} debian@10.30.133.80 'sudo systemctl stop  tomcat'".format(args.cbioportal_key),
                    shell=True)
    os.wait()
    subprocess.call("ssh -i {} debian@10.30.133.80 'sudo systemctl start tomcat'".format(args.cbioportal_key),
                    shell=True)
    helper.working_on(verb)


def main():
    args = define_parser().parse_args()
    verb = args.verbose
    force = args.force

    study_config_file = get_config(args.study_info, 'study', verb)

    information = []
    for index, row in study_config_file.data_frame.iterrows():
        row[1] = os.path.join(os.path.dirname(os.path.abspath(args.study_info)), row[1])
        information.append(get_config(row[1], row[0], verb))

    [print(a) for a in information] if verb else print(),

    samples_config = Config.Config(c for c in information if c.type_config == 'sample')
    print(samples_config)

    for each in information:
        generate_meta_file(each, study_config_file, verb)
        generate_data_file(each, study_config_file, force, verb)
        generate_case_list(each, study_config_file)
    generate_meta_study(study_config_file, verb)

    helper.stars()
    helper.working_on(verb, message='CONGRATULATIONS! A minimal study is now be complete!')
    helper.stars()


if __name__ == '__main__':
    main()
