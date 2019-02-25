__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import argparse
import subprocess
import os

import pandas as pd
import numpy as np

# Other Scripts
import generate_data_meta_cancer_type
import generate_data_meta_mutation_data
import helper
import Config

meta_info_map = {'mutation':    ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
                 'sample':      ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 'patient':     ['CLINICAL', 'PATIENT_ATTRIBUTES'],
                 'cancer_type': ['CANCER_TYPE', 'CANCER_TYPE']}

# TODO:: Add all the other data types.
# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4

# A set of default ordered values all meta files have to a certain extent
global_zip = ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']

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
    required.add_argument("-k", "--key",
                          type=lambda key: os.path.abspath(key),
                          help="The RSA key to cBioPortal. Should have appropriate read write restrictions",
                          metavar='FILE',
                          default='/u/kchandan/cbioportal.pem')
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


def get_config(file, f_type, verb) -> Config.Config:
    if os.path.isfile(file):
        print('File Name: {}'.format(file))
    else:
        raise OSError('ERROR: Is not a file\n' + file)
    f = open(file, 'r')

    helper.working_on(verb, message='Reading information\n')
    file_map = {}
    for line in f:
        if line[0] == '#':
            line = line.strip().replace('#', '').split('=')
            file_map[line[0]] = line[1]
        else:
            break
    f.close()
    data_frame = pd.read_csv(file, delimiter='\t', skiprows=len(file_map), dtype=object)
    config_file = Config.Config(file_map, data_frame, f_type)
    return config_file


def get_config_clinical(file: str, f_type: str, verb) -> Config.ClinicalConfig:
    if os.path.isfile(file):
        print('File Name: {}'.format(file))
    else:
        raise OSError('ERROR: Is not a file\n' + file)
    f = open(file, 'r')

    helper.working_on(verb, message='Reading information\n')
    file_map = {}
    data_frame = []
    for line in f:
        if line[0] == '#':
            line = line.strip().replace('#', '').split('=')
            file_map[line[0]] = line[1]
        else:
            data_frame.append(line.strip().split('\t'))
    config_file = Config.ClinicalConfig(file_map, data_frame, f_type)
    return config_file


def generate_meta_file(meta_config: Config.Config, study_config: Config.Config, verb):
    # NOTE:: Should be able to generate any from the set of all meta files

    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(study_config.config_map['output_folder'])
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
    original_dir = helper.change_folder(study_config.config_map['output_folder'])
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
        meta_config = generate_data_meta_mutation_data.export2maf(meta_config, force, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Concatenating .maf files...')
        generate_data_meta_mutation_data.concat_files_maf(meta_config, study_config)
        helper.working_on(verb)

    elif meta_config.type_config == 'cancer_type':
        helper.working_on(verb, message='Reading colours...')
        colours = generate_data_meta_cancer_type.get_colours()
        helper.working_on(verb)

        helper.working_on(verb, message='Generating cancer_type records...')
        generate_data_meta_cancer_type.gen_cancer_type_data(meta_config, study_config, colours)
        helper.working_on(verb)


def generate_case_list(meta_config: Config.Config, study_config: Config.Config):
    if meta_config.type_config in case_list_map.keys():
        case_list_folder = os.path.join(study_config.config_map['output_folder'], 'case_lists')
        if not os.path.exists(case_list_folder):
            os.makedirs(case_list_folder)

        f = open('{}/data_{}{}.txt'.format(case_list_folder,
                                           meta_config.type_config,
                                           case_list_map[meta_config.type_config]), 'w')

        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'],
                                           case_list_map[meta_config.type_config]))
        f.write('case_list_name: {}\n'.format(meta_config.config_map['profile_name']))
        f.write('case_list_description: {}\n'.format(meta_config.config_map['profile_description']))
        f.write('case_list_ids: {}\n'.format('\t'.join(np.append(meta_config.data_frame['TUMOR_COL'],
                                                                 meta_config.data_frame['NORMAL_COL']))))
        f.flush()
        os.fsync(f)
        f.close()


def generate_data_clinical(samples_config: Config.ClinicalConfig, study_config: Config.Config, verb):
    num_header_lines = 4

    helper.working_on(verb, message='Writing to data_{}.txt ...'.format(samples_config.type_config))

    output_file = os.path.join(os.path.abspath(study_config.config_map['output_folder']),
                               'data_{}.txt'.format(samples_config.type_config))

    array = np.array(samples_config.data_frame)

    f = open(output_file, 'w')
    for i in range(array.shape[0]):
        if i < num_header_lines:
            f.write('#{}\n'.format('\t'.join(samples_config.data_frame[i])))
        else:
            f.write('{}\n'.format('\t'.join(samples_config.data_frame[i])))
    f.close()
    helper.working_on(verb)


def export_study_to_cbioportal(key, study_folder, verb):
    folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Copying folder to cBioPortal instance at 10.30.133.80 ...')

    # Cleanup Location
    print("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
          "rm -r ~/oicr_studies/{}; "
          "mkdir ~/oicr_studies/{}'".format(key,
                                            folder,
                                            folder
                                            )) if verb else print(),
    subprocess.call("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                    "rm -r ~/oicr_studies/{}; "
                    "mkdir ~/oicr_studies/{}'".format(key,
                                                      folder,
                                                      folder
                                                      ),
                    shell=True)
    # Copy over
    print('scp -r -i {} {} debian@10.30.133.80:/home/debian/oicr_studies/'.format(key, study_folder)) if verb else print(),
    subprocess.call('scp -r -i {} {} debian@10.30.133.80:/home/debian/oicr_studies/'.format(key, study_folder),
                    shell=True)
    helper.working_on(verb)

    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')

    print("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
          "./metaImport.py -s ~/oicr_studies/{} "
          "-u http://10.30.133.80:8080/cbioportal "
          "-o'".format(key, folder)) if verb else print(),
    subprocess.call("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                    "sudo ./metaImport.py -s ~/oicr_studies/{} "
                    "-u http://10.30.133.80:8080/cbioportal "
                    "-o'".format(key,
                                 folder,),
                    shell=True)

    print("ssh -i {} debian@10.30.133.80 'sudo systemctl stop  tomcat'".format(key)) if verb else print(),
    subprocess.call("ssh -i {} debian@10.30.133.80 'sudo systemctl stop  tomcat'".format(key),
                    shell=True)

    print("ssh -i {} debian@10.30.133.80 'sudo systemctl start tomcat'".format(key)) if verb else print(),
    subprocess.call("ssh -i {} debian@10.30.133.80 'sudo systemctl start tomcat'".format(key),
                    shell=True)


    helper.working_on(verb)


def main():
    args = define_parser().parse_args()
    verb = args.verbose
    force = args.force

    study_config_file = get_config(args.study_info, 'study', verb)

    information = []
    clinic_data = []
    cancer_type = ''

    for i in range(int(study_config_file.data_frame.shape[0])):
        config_file_name = os.path.join(os.path.dirname(os.path.abspath(args.study_info)),
                                        study_config_file.data_frame.iloc[i][int(1)])

        config_file_type = study_config_file.data_frame.iloc[i][int(0)]

        if study_config_file.data_frame.iloc[i][0] in ['sample', 'patient']:
            clinic_data.append(get_config_clinical(config_file_name,
                                                   config_file_type,
                                                   verb))
        elif study_config_file.data_frame.iloc[i][0] in ['cancer_type']:
            cancer_type = get_config(config_file_name,
                                     config_file_type,
                                     verb)
        else:
            information.append(get_config(config_file_name,
                                          config_file_type,
                                          verb))

    [print('Information File {}:\n{}\n'.format(a.type_config, a)) for a in information] if verb else print(),
    [print('\nClinical Files {}:\n{}\n'.format(a.type_config, a)) for a in clinic_data] if verb else print(),

    helper.clean_folder(study_config_file.config_map['output_folder'])

    if cancer_type:
        generate_meta_file(cancer_type, study_config_file, verb)
        generate_data_file(cancer_type, study_config_file, force, verb)
    for each in clinic_data:
        generate_meta_file(each, study_config_file, verb)
        generate_data_clinical(each, study_config_file, verb)
    for each in information:
        generate_meta_file(each, study_config_file, verb)
        generate_data_file(each, study_config_file, force, verb)
        generate_case_list(each, study_config_file)
    generate_meta_study(study_config_file, verb)

    export_study_to_cbioportal(args.key, study_config_file.config_map['output_folder'], verb)

    helper.stars()
    helper.working_on(verb, message='CONGRATULATIONS! A minimal study is now be complete!')
    helper.working_on(verb, message='Output folder: {}'.format(study_config_file.config_map['output_folder']))
    helper.stars()


if __name__ == '__main__':
    main()
