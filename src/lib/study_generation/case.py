__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os

from lib.constants.constants import case_list_map
from lib.support import Config


def generate_case_list(meta_config: Config.Config, study_config: Config.Config):
    if meta_config.type_config in case_list_map.keys():
        case_list_folder = os.path.join(study_config.config_map['output_folder'], 'case_lists/')
        if not os.path.exists(case_list_folder):
            os.makedirs(case_list_folder)

        f = open(os.path.join(case_list_folder, 'cases{}.txt'.format(case_list_map[meta_config.type_config])), 'w')

        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'],
                                           case_list_map[meta_config.type_config]))
        try:
            f.write('case_list_name: {}\n'.format(meta_config.config_map['profile_name']))
            f.write('case_list_description: {}\n'.format(meta_config.config_map['profile_description']))
        except KeyError:
            raise KeyError('Missing Profile_Name or Profile_Description from {} file'.format(meta_config.type_config))
        f.write('case_list_ids: {}\n'.format('\t'.join(meta_config.data_frame['TUMOR_ID'])))
        f.flush()
        f.close()