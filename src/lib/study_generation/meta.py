__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os

from lib.constants import meta_info_map, general_zip, ref_gene_id_zip, config2name_map
from lib.support import Config, helper


def generate_meta_type(meta_config: Config.Config, study_config: Config.Config, verb):
    # NOTE:: Should be able to generate any from the set of all meta files
    # TODO:: Add functionality for optional fields
    # TODO:: Potentially redo entire function

    helper.working_on(verb, message='Saving meta_{}.txt ...'.format(config2name_map[meta_config.type_config]))

    f_out = os.path.join(study_config.config_map['output_folder'],
                         'meta_{}.txt'.format(config2name_map[meta_config.type_config]))
    f = open(f_out, 'w')

    if not meta_config.type_config == 'CANCER_TYPE':
        # CANCER_TYPE meta file is the only one not to contain the identifier with the meta-data
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))

    # Write genetic_alteration_type, datatype, stable_id, reference_genome and other values
    if meta_config.type_config == 'MRNA_EXPRESSION':
        for field, entry in zip(general_zip, meta_info_map[meta_config.type_config]):
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


def generate_meta_study(study_config: Config.Config, verb):

    output_meta = os.path.join(study_config.config_map['output_folder'], 'meta_study.txt')
    helper.working_on(verb, message='Saving meta_study.txt ...')

    f = open(output_meta, 'w')

    f.write('type_of_cancer: {}\n'.format(study_config.config_map['type_of_cancer']))
    f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
    f.write('name: {}\n'.format(study_config.config_map['name']))
    f.write('short_name: {}\n'.format(study_config.config_map['short_name']))
    f.write('description: {}\n'.format(study_config.config_map['description']))
    f.write('add_global_case_list: true\r')
    f.flush()
    f.close()

    helper.working_on(verb)