__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import argparse
import subprocess
import os

import typing
import pandas as pd
import numpy as np

# Other Scripts
import cancer_type
import mutation_data
import helper
import Config


Information = typing.List[Config.Config]
meta_info_map = {'MAF':                 ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
                 'SEG':                 ['COPY_NUMBER_ALTERATION', 'SEG', 'hg19'],
                 'GEP':                 ['MRNA_EXPRESSION', 'CONTINUOUS'],
                 'SAMPLE_ATTRIBUTES':   ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 'PATIENT_ATTRIBUTES':  ['CLINICAL', 'PATIENT_ATTRIBUTES'],
                 'CANCER_TYPE':         ['CANCER_TYPE', 'CANCER_TYPE']}

# TODO:: Add all the other data types.
# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4

# A set of default ordered values all meta files have to a certain extent
general_zip =     ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']
ref_gene_id_zip = ['genetic_alteration_type', 'datatype', 'reference_genome_id']

case_list_map =   {'MAF': '_sequenced',
                   'DISCRETE': '_cna'}
cbiowrap_export = ['MAF', 'SEG', 'GEP']

config2name_map = {'MAF':                 'mutations_extended',
                   'SEG':                 'segments',
                   'GEP':                 'log2CNA',
                   'SAMPLE_ATTRIBUTES':   'clinical_samples',
                   'PATIENT_ATTRIBUTES':  'clinical_patients',
                   'CANCER_TYPE':         'cancer_type'}
# dCNA => discrete Copy Number Variation


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="CbiOportal Wrapper TOol (COWTOwn) "
                                                 "(https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool that "
                                                 "interfaces with cBioWrap to generate an importable study for a "
                                                 "cBioPortal instance.  ")

    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-o", "--study-output-folder",
                          type=lambda folder: os.path.abspath(folder),
                          help="The main folder of the study you want to generate.",
                          metavar='FOLDER',
                          default='new_study/')
    required.add_argument("-s", "--study-info",
                          help="The location of the study input information",
                          metavar='FILE')
    parser.add_argument("-k", "--key",
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


def generate_meta_file(meta_config: Config.Config, study_config: Config.Config, verb):
    # NOTE:: Should be able to generate any from the set of all meta files

    helper.working_on(verb, message='Changing folder...')
    original_dir = helper.change_folder(study_config.config_map['output_folder'])
    helper.working_on(verb)

    # TODO:: Add functionality for optional fields

    helper.working_on(verb, message='Saving meta_{}.txt ...'.format(config2name_map[meta_config.type_config]))

    f_out = 'meta_{}.txt'.format(config2name_map[meta_config.type_config])
    f = open(f_out, 'w')

    if not meta_config.type_config == 'CANCER_TYPE':
        # CANCER_TYPE meta file is the only one not to contain the identifier with the meta-data
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))

    # Write genetic_alteration_type, datatype, stable_id, reference_genome and other values
    if meta_config.type_config == 'MRNA_EXPRESSION':
        for field, entry in zip(general_zip[:3] + ['source_stable_id'] + general_zip[3:],
                                meta_info_map[meta_config.type_config]):
            f.write('{}: {}\n'.format(field, entry))

    elif meta_config.type_config in ['SEG', 'GISTIC']:
        for field, entry in zip(ref_gene_id_zip, meta_info_map[meta_config.type_config]):
            f.write('{}: {}\n'.format(field, entry))
        if meta_config.type_config == 'SEG':
            f.write('{}: {}\n'.format('description', meta_config.config_map['description']))

    else:
        for field, entry in zip(general_zip, meta_info_map[meta_config.type_config]):
            f.write('{}: {}\n'.format(field, entry))

    # Add profile_name and description, but exclude clinical data
    if meta_config.type_config not in ['SAMPLE_ATTRIBUTES', 'PATIENT_ATTRIBUTES']:
        if all([i in meta_config.config_map for i in ['profile_name', 'profile_description']]):
            f.write('profile_name: {}\n'.format(meta_config.config_map['profile_name']))
            f.write('profile_description: {}\n'.format(meta_config.config_map['profile_description']))

    f.write('data_filename: data_{}.txt\n'.format(config2name_map[meta_config.type_config]))
    f.flush()
    f.close()
    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! {} meta has been saved!'.format(config2name_map[meta_config.type_config]))


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
    f.close()

    helper.working_on(verb)

    helper.working_on(verb, message='Popping back...')
    helper.reset_folder(original_dir)
    helper.working_on(verb, message='Success! The cancer study meta has been saved!')


def generate_data_file(meta_config: Config.Config, study_config: Config.Config, force, verb):

    if meta_config.type_config == 'MAF':
        helper.working_on(verb, message='Gathering and decompressing MAF files into temporary folder...')
        mutation_data.decompress_to_temp(meta_config, verb)
        helper.working_on(verb)

        if meta_config.config_map['caller'] == 'Strelka':
            # Do some pre-processing
            print('Something should be done')
        elif meta_config.config_map['caller'] in 'GATKHaplotypeCaller':
            # Do some other sort of pre-processing
            print('Something else should be done')

        helper.working_on(verb, message='Exporting vcf2maf...')
        helper.working_on(verb, message='And deleting .vcf s...')
        meta_config = mutation_data.export2maf(meta_config, force, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Generating wanted_columns.txt file for cBioWrap...')
        mutation_data.wanted_columns(meta_config, study_config)
        helper.working_on(verb)

        print(meta_config)
        helper.working_on(verb, message='Re-zipping .mafs for cBioWrap ...')
        meta_config = mutation_data.zip_maf_files(meta_config, force)
        helper.working_on(verb)
        print(meta_config)

    elif meta_config.type_config == 'SEG':
        helper.working_on(verb, message='Gathering and decompressing SEG files into temporary folder')
        mutation_data.decompress_to_temp(meta_config, verb)
        helper.working_on(verb)

    elif meta_config.type_config == 'CANCER_TYPE':
        helper.working_on(verb, message='Reading colours...')
        colours = cancer_type.get_colours()
        helper.working_on(verb)

        helper.working_on(verb, message='Generating CANCER_TYPE records...')
        cancer_type.gen_cancer_type_data(meta_config, study_config, colours)
        helper.working_on(verb)


def generate_data_clinical(samples_config: Config.ClinicalConfig, study_config: Config.Config, verb):
    num_header_lines = 4

    helper.working_on(verb, message='Writing to data_{}.txt ...'.format(config2name_map[samples_config.type_config]))

    output_file = os.path.join(os.path.abspath(study_config.config_map['output_folder']),
                               'data_{}.txt'.format(config2name_map[samples_config.type_config]))

    array = np.array(samples_config.data_frame)

    f = open(output_file, 'w')
    for i in range(array.shape[0]):
        if i < num_header_lines:
            f.write('#{}\n'.format('\t'.join(samples_config.data_frame[i])))
        else:
            f.write('{}\n'.format('\t'.join(samples_config.data_frame[i])))
    f.close()
    helper.working_on(verb)


def generate_case_list(meta_config: Config.Config, study_config: Config.Config):
    if meta_config.type_config in case_list_map.keys():
        case_list_folder = os.path.join(study_config.config_map['output_folder'], 'case_lists')
        if not os.path.exists(case_list_folder):
            os.makedirs(case_list_folder)

        f = open('{}/data_{}{}.txt'.format(case_list_folder,
                                           config2name_map[meta_config.type_config],
                                           case_list_map[meta_config.type_config]), 'w')

        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'],
                                           case_list_map[meta_config.type_config]))
        f.write('case_list_name: {}\n'.format(meta_config.config_map['profile_name']))
        f.write('case_list_description: {}\n'.format(meta_config.config_map['profile_description']))
        f.write('case_list_ids: {}\n'.format('\t'.join(meta_config.data_frame['TUMOR_ID'])))
        f.flush()
        f.close()


def generate_cbiowrap_configs(information: Information, study_config: Config.Config, verb):
    # Copy fixed config.
    ini = open('config_fixed.ini', 'r')
    fixed = ini.readlines()
    ini.close()

    # Write wanted_columns.txt
    helper.working_on(verb, 'Writing wanted at {}'.format(helper.get_cbiowrap_file(study_config, 'wanted_columns.txt')))
    if 'MAF' not in [each.type_config for each in information]:
        wanted = helper.get_cbiowrap_file(study_config, 'wanted_columns.txt')
        helper.clean_folder(os.path.dirname(wanted))
        o = open(wanted, 'w+')
        o.write('')
        o.flush()
        o.close()

    info = information.copy()
    print([a for a in info])
    print([a for a in information])
    for each in info:
        if each.type_config in cbiowrap_export:
            for i in range(each.data_frame.shape[0]):
                each.data_frame['FILE_NAME'][i] = os.path.join(each.config_map['input_folder'],
                                                               each.data_frame['FILE_NAME'][i])

    # Generate Mapping.csv
    [i.data_frame.rename(columns={'FILE_NAME': i.type_config}, inplace=True) for i in info]
    # Merge all data_frames, and gather mutation, seg and gep
    # TODO:: Convert the TUMOR_ID to a SAMPLE_ID
    if len(info) == 0:
        result = Config.Config({}, pd.DataFrame('PATIENT_ID', 'TUMOR_ID'), '')
    elif len(info) == 1:
        result = info[0]
    else:
        result = info[0]
        for i in range(1, len(info)):
            result.data_frame = pd.merge(result.data_frame, info[i].data_frame, on=['PATIENT_ID', 'TUMOR_ID'])

    result.data_frame.replace(np.nan, 'NA', inplace=True)

    for col in cbiowrap_export:
        if col not in result.data_frame:
            result.data_frame[col] = 'NA'

    print(result)
    csv = result.data_frame[['PATIENT_ID', 'TUMOR_ID', *cbiowrap_export]]
    print(csv)
    helper.working_on(verb, 'Writing mapping.csv at {}'.format(helper.get_cbiowrap_file(study_config, 'mapping.csv')))
    csv.to_csv(helper.get_cbiowrap_file(study_config, 'mapping.csv'), header=False, index=False)
    # Write arguments to config.ini
    helper.working_on(verb, 'Writing Config.ini at {}'.format(helper.get_cbiowrap_file(study_config, 'config.ini')))
    out = open(helper.get_cbiowrap_file(study_config, 'config.ini'), 'w+')
    out.writelines(fixed)
    out.write('\nstudy="{}"'.format(study_config.config_map['cancer_study_identifier']))
    out.write('\ntypec="{}"'.format(study_config.config_map['type_of_cancer']))
    out.write('\noutdir="{}"'.format(study_config.config_map['output_folder']))
    out.write('\nvepkeep="{}"'.format(helper.get_cbiowrap_file(study_config, 'wanted_columns.txt')))
    out.write('\nmapfile="{}"'.format(helper.get_cbiowrap_file(study_config, 'mapping.csv')))


def run_cbiowrap(study_config: Config.Config):
    subprocess.call('cd /.mounts/labs/gsiprojects/gsi/cBioGSI/kchandan/cBioWrap/; '
                    './cBioWrap.sh -c {}'.format(helper.get_cbiowrap_file(study_config, 'config.ini')),
                    shell=True)


def export_study_to_cbioportal(key, study_folder, verb):
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Copying folder to cBioPortal instance at 10.30.133.80 ...')

    # Cleanup Location
    helper.working_on(verb, "ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                            "rm -r ~/oicr_studies/{}; "
                            "mkdir ~/oicr_studies/{}'".format(key, base_folder, base_folder))

    subprocess.call("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                    "rm -r ~/oicr_studies/{}; "
                    "mkdir ~/oicr_studies/{}'".format(key,
                                                      base_folder,
                                                      base_folder
                                                      ),
                    shell=True)
    # Copy over
    helper.working_on(verb, 'scp -r -i {} {} debian@10.30.133.80:/home/debian/oicr_studies/ '.format(key, study_folder))
    subprocess.call('scp -r -i {} {} debian@10.30.133.80:/home/debian/oicr_studies/'.format(key, study_folder),
                    shell=True)
    helper.working_on(verb)

    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')

    print("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
          "./metaImport.py -s ~/oicr_studies/{} "
          "-u http://10.30.133.80:8080/cbioportal "
          "-o'".format(key, base_folder)) if verb else print(),
    subprocess.call("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                    "sudo ./metaImport.py -s ~/oicr_studies/{} "
                    "-u http://10.30.133.80:8080/cbioportal "
                    "-o'".format(key,
                                 base_folder),
                    shell=True)

    helper.working_on(verb, "ssh -i {} debian@10.30.133.80 'sudo systemctl stop  tomcat'".format(key))
    subprocess.call("ssh -i {} debian@10.30.133.80 'sudo systemctl stop  tomcat'".format(key), shell=True)

    helper.working_on(verb, "ssh -i {} debian@10.30.133.80 'sudo systemctl start tomcat'".format(key))
    subprocess.call("ssh -i {} debian@10.30.133.80 'sudo systemctl start tomcat'".format(key), shell=True)

    helper.working_on(verb)


def main():
    args = define_parser().parse_args()
    verb = args.verbose
    force = args.force

    study_config = Config.get_config(args.study_info, 'study', verb)

    information = []
    clinic_data = []
    cancer_type = []

    # Gather Config files
    for i in range(int(study_config.data_frame.shape[0])):
        config_file_name = os.path.join(os.path.dirname(os.path.abspath(args.study_info)),
                                        study_config.data_frame['FILE'][i])

        config_file_type = study_config.data_frame['TYPE'][i]

        if study_config.data_frame.iloc[i][0] in ['SAMPLE_ATTRIBUTES', 'PATIENT_ATTRIBUTES']:
            clinic_data.append(Config.get_config_clinical(config_file_name,
                                                          config_file_type,
                                                          verb))
        elif study_config.data_frame.iloc[i][0] in ['CANCER_TYPE']:
            cancer_type = Config.get_config(config_file_name,
                                            config_file_type,
                                            verb)
        else:
            information.append(Config.get_config(config_file_name,
                                                 config_file_type,
                                                 verb))

    [print('Information File {}:\n{}\n'.format(a.type_config, a)) for a in information] if verb else print(),
    [print('\nClinical Files {}:\n{}\n'.format(a.type_config, a)) for a in clinic_data] if verb else print(),

    # Clean Output Folder/Initialize it
    helper.clean_folder(study_config.config_map['output_folder'])

    for each in information:
        # Convert vcf to maf
        generate_data_file(each, study_config, force, verb)

    # Generate Config.ini file, Mapping.csv and wanted_columns.txt
    generate_cbiowrap_configs(information, study_config, verb)

    # run cBioWrap.sh
    run_cbiowrap(study_config)

    os.rename(os.path.join(study_config.config_map['output_folder'], 'cbioportal_import_data'),
              os.path.join(study_config.config_map['output_folder'], study_config.config_map['cancer_study_identifier']))

    study_config.config_map['output_folder'] = os.path.join(study_config.config_map['output_folder'],
                                                            study_config.config_map['cancer_study_identifier'])
    # Overwrite some of the meta files (Optional)
    # Generate CANCER_TYPE
    if type(cancer_type) == Config.Config:
        generate_meta_file(cancer_type, study_config, verb)
        generate_data_file(cancer_type, study_config, force, verb)
    for each in information:
        generate_meta_file(each, study_config, verb)
    for each in clinic_data:
        generate_meta_file(each, study_config, verb)
        generate_data_clinical(each, study_config, verb)
    generate_meta_study(study_config, verb)

    # export to cbioportal!
    export_study_to_cbioportal(args.key, study_config.config_map['output_folder'], verb)

    helper.stars()
    helper.working_on(verb, message='CONGRATULATIONS! A minimal study is now be complete!')
    helper.working_on(verb, message='Output folder: {}'.format(study_config.config_map['output_folder']))
    helper.stars()


if __name__ == '__main__':
    main()
