__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

from collections import OrderedDict
import os

from lib.constants.constants import meta_info_map, general_zip, ref_gene_id_zip, config2name_map, clinical_type, optional_fields
from lib.support import Config, helper


#def generate_meta_type(config_type: str, config_map: dict, study_config: Config.Config, verb):
def generate_meta_type(meta_config: Config.Config, study_config: Config.Config, verb):
    # NOTE:: Should be able to generate any from the set of all meta files

    output_set = []

    ####################### BEGIN WRITING META_FILES ###########################
    helper.working_on(verb, message='Saving meta_{}.txt ...'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))

    if not meta_config.datahandler == 'CANCER_TYPE':
        # CANCER_TYPE meta file is the only one not to contain the identifier with the meta-data
        output_set.append(['cancer_study_identifier', study_config.config_map['cancer_study_identifier']])

    # Write genetic_alteration_type, datahandler, stable_id, reference_genome and other values
    if meta_config.datahandler in ['SEG', 'GISTIC_2']:
        for field, entry in zip(ref_gene_id_zip, meta_info_map[meta_config.alterationtype + ":" + meta_config.datahandler]):
            output_set.append((field, entry))
        if meta_config.datahandler == 'SEG':
            try:
                output_set.append(('description', meta_config.config_map['description']))
            except KeyError:
                print('Using Profile_Description instead of description because it is missing from type_config file.')
                output_set.append(('description', meta_config.config_map['profile_description']))
    else:

        for field, entry in zip(general_zip, meta_info_map[meta_config.alterationtype + ":" + meta_config.datahandler]):
            output_set.append((field, entry))

    # Add profile_name and description, but exclude clinical data
    if meta_config.datahandler not in clinical_type and meta_config.datahandler not in ['SEG']:
        if all([i in meta_config.config_map for i in ['profile_name', 'profile_description']]):
            output_set.append(('profile_name', meta_config.config_map['profile_name']))
            output_set.append(('profile_description', meta_config.config_map['profile_description']))

    for x in (set(meta_config.config_map.keys()) & set(optional_fields)):
        output_set.append((x, config_map[x]))

    output_set.append(('data_filename', 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])))

    # Overwrite settings from config
    output_set = OrderedDict(output_set)
    for i in set(meta_config.config_map.keys()) & set(output_set.keys()):
        output_set[i] = meta_config.config_map[i]

    f_out = os.path.join(study_config.config_map['output_folder'],
                         'meta_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    f = open(f_out, 'w')

    f.write('\n'.join(['{}: {}'.format(i, output_set[i]) for i in output_set]))
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
