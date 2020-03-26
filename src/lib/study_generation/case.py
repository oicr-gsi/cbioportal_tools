__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os

from lib.constants.constants import case_list_map
from lib.study_generation import data
from lib.support import Config


def generate_case_list(meta_config: Config.Config, study_config: Config.Config, verb):
    if meta_config.datahandler in case_list_map.keys():
        case_list_folder = os.path.join(study_config.config_map['output_folder'], 'case_lists/')
        if not os.path.exists(case_list_folder):
            os.makedirs(case_list_folder)

        if 'suffix' in meta_config.config_map.keys():
            suffix = meta_config.config_map['suffix']
        else:
            suffix = case_list_map[meta_config.datahandler]

        f = open(os.path.join(case_list_folder, 'cases{}.txt'.format(suffix)), 'w')

        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'], suffix))
        try:
            f.write('case_list_name: {}\n'.format(meta_config.config_map['profile_name']))
            f.write('case_list_description: {}\n'.format(meta_config.config_map['profile_description']))
        except KeyError:
            raise KeyError('Missing Profile_Name or Profile_Description from {} file'.format(meta_config.datahandler))
        try:
            ids = meta_config.data_frame['SAMPLE_ID']
        except KeyError:
            # If pipeline is FILE, this will probably happen
            ids = data.get_sample_ids(meta_config, verb)
        f.write('case_list_ids: {}\n'.format('\t'.join(ids)))
        f.flush()
        f.close()

        # Generate cnaseq case list if there is already cases_cna (CNA data) and cases_sequenced (mutation data)
        if os.path.isfile(os.path.join(case_list_folder, 'cases_cna.txt') and os.path.isfile(os.path.join(case_list_folder, 'cases_sequenced.txt')\
                and os.path.isfile(os.path.join(case_list_folder, 'cases_cnaseq.txt') == False:
            f = open(os.path.join(case_list_folder, 'cases_cnaseq.txt'.format(suffix)), 'w')
            f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
            f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'], '_cnaseq'))        
            f.write('case_list_name: {}\n'.format('Samples profiled for cnas and sequencing'))
            f.write('case_list_description: {}\n'.format('This is this case list that contains all samples that are profiled for mutations and cnas.'))
            try:
                ids = meta_config.data_frame['SAMPLE_ID']
            except KeyError:
                # If pipeline is FILE, this will probably happen
                ids = data.get_sample_ids(meta_config, verb)
            f.write('case_list_ids: {}\n'.format('\t'.join(ids)))
            f.flush()
            f.close()

        if os.path.isfile(os.path.join(case_list_folder, 'cases_cna.txt') and os.path.isfile(os.path.join(case_list_folder, 'cases_sequenced.txt')\
                and os.path.isfile(os.path.join(case_list_folder, 'cases_rna_seq_mrna.txt') and os.path.isfile(os.path.join(case_list_folder, 'cases__3way_complete.txt') == False:
            f = open(os.path.join(case_list_folder, 'cases__3way_complete.txt'.format(suffix)), 'w')
            f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
            f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'], '_3way_complete'))
            f.write('case_list_name: {}\n'.format'Samples profiled for all of mutation, cnas, and rnaseq'))
            f.write('case_list_description: {}\n'.format('This is this case list that contains all samples that are profiled for mutations, cnas, and rnaseq.'))
            try:
                ids = meta_config.data_frame['SAMPLE_ID']
            except KeyError:
                # If pipeline is FILE, this will probably happen
                ids = data.get_sample_ids(meta_config, verb)
            f.write('case_list_ids: {}\n'.format('\t'.join(ids)))
            f.flush()
            f.close()
