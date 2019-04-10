__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os

from lib.constants.constants import meta_info_map, general_zip, ref_gene_id_zip, config2name_map, clinical_type
from lib.support import Config, helper


def generate_meta_type(config_type: str, config_map: dict, study_config: Config.Config, verb):
    # NOTE:: Should be able to generate any from the set of all meta files
    #TODO:: Add functionality for optional fields
    # Would require list of optional fields that then map onto their names then printed onto the meta file

    ####################### BEGIN WRITING META_FILES ###########################
    helper.working_on(verb, message='Saving meta_{}.txt ...'.format(config2name_map[config_type]))

    f_out = os.path.join(study_config.config_map['output_folder'],
                         'meta_{}.txt'.format(config2name_map[config_type]))
    f = open(f_out, 'w')

    if not config_type == 'CANCER_TYPE':
        # CANCER_TYPE meta file is the only one not to contain the identifier with the meta-data
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))

    # Write genetic_alteration_type, datatype, stable_id, reference_genome and other values
    if config_type == 'MRNA_EXPRESSION':
        for field, entry in zip(general_zip, meta_info_map[config_type]):
            f.write('{}: {}\n'.format(field, entry))

    elif config_type in ['SEG', 'GISTIC_2.0']:
        for field, entry in zip(ref_gene_id_zip, meta_info_map[config_type]):
            f.write('{}: {}\n'.format(field, entry))
        if config_type == 'SEG':
            try:
                f.write('{}: {}\n'.format('description', config_map['description']))
            except KeyError:
                print('Using Profile_Description instead of description because it is missing from type_config file.')
                f.write('{}: {}\n'.format('description', config_map['profile_description']))
    else:
        for field, entry in zip(general_zip, meta_info_map[config_type]):
            f.write('{}: {}\n'.format(field, entry))

    # Add profile_name and description, but exclude clinical data
    if config_type not in [clinical_type, 'SEG']:
        if all([i in config_map for i in ['profile_name', 'profile_description']]):
            f.write('profile_name: {}\n'.format(config_map['profile_name']))
            f.write('profile_description: {}\n'.format(config_map['profile_description']))

    f.write('data_filename: data_{}.txt\n'.format(config2name_map[config_type]))
    f.flush()
    f.close()
    helper.working_on(verb)


def generate_meta_study(study_config: Config.Config, verb):

    output_meta = os.path.join(study_config.config_map['output_folder'], 'meta_study.txt')
    helper.working_on(verb, message='Saving meta_study.txt ...')

    f = open(output_meta, 'w')

    try:
        f.write('type_of_cancer: {}\n'.format(study_config.config_map['type_of_cancer']))
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('name: {}\n'.format(study_config.config_map['name']))
        f.write('short_name: {}\n'.format(study_config.config_map['short_name']))
        f.write('description: {}\n'.format(study_config.config_map['description']))
        f.write('add_global_case_list: true\r')
    except KeyError as key:
        helper.stars()
        helper.stars()
        print('The study config is missing a value, please add it. \n{}'.format(key.with_traceback()))
        helper.stars()
        helper.stars()
    f.flush()
    f.close()

    helper.working_on(verb)