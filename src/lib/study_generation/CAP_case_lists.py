import os

from lib.constants.constants import case_list_map
from lib.study_generation import data
from lib.support import Config


def case_list_handler(information, custom_list, study_config: Config.Config, verb):
    case_list_folder = os.path.join(study_config.config_map['output_folder'], 'case_lists/')
    if not os.path.exists(case_list_folder):
            os.makedirs(case_list_folder)
   
    # generate the case lists for the datatypes in information
    generate_case_lists(information, study_config, case_list_folder, verb)

    # if custom_list isn't empty then generate custom case list
    generate_case_lists(custom_list, study_config, case_list_folder, verb)
    
    # Generate cnaseq case list if there is already cases_cna (CNA data) and cases_sequenced (mutation data)
    if os.path.isfile(os.path.join(case_list_folder, 'cases_cna.txt')) and os.path.isfile(os.path.join(case_list_folder, 'cases_sequenced.txt')):
        suffix = '_cnaseq'
        datahandler_suffixes = ['_sequenced', '_cna']
        generate_multi_case_lists(information, study_config, case_list_folder, suffix, datahandler_suffixes, verb)
    
    # Generate 3way_complete case list if there is already cases_sequences (mutation data) cases_cna (cna data) and cases_rna_seq_mrna (expression data)
    if os.path.isfile(os.path.join(case_list_folder, 'cases_cna.txt')) and os.path.isfile(os.path.join(case_list_folder, 'cases_sequenced.txt')) and os.path.isfile(os.path.join(case_list_folder, 'cases_rna_seq_mrna.txt')):
        suffix = '_3way_complete'
        datahandler_suffixes = ['_sequenced', '_cna', '_rna_seq_mrna']
        generate_multi_case_lists(information, study_config, case_list_folder, suffix, datahandler_suffixes, verb)

def generate_case_lists(information, study_config, case_list_folder, verb):
    for meta_config in information:
        if meta_config.datahandler in case_list_map.keys():
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
    
def generate_multi_case_lists(information, study_config, case_list_folder, suffix, datahandler_suffixes, verb):
        f = open(os.path.join(case_list_folder, 'cases{}.txt'.format(suffix)), 'w')
        
        f.write('cancer_study_identifier: {}\n'.format(study_config.config_map['cancer_study_identifier']))
        f.write('stable_id: {}{}\n'.format(study_config.config_map['cancer_study_identifier'], suffix))        
        
        f.write('case_list_name: {}\n'.format('Samples profiled for cnas and sequencing'))
        f.write('case_list_description: {}\n'.format('This is this case list that contains all samples that are profiled for mutations and cnas.'))
        
        all_ids = ''
        for meta_config in information:
            if meta_config.datahandler in case_list_map.keys():
                if case_list_map[meta_config.datahandler] in datahandler_suffixes:
                    ids = meta_config.data_frame['SAMPLE_ID']
                    compare = all_ids.split(sep='\t')
                    ids = ids[~ids.isin(compare)]
                    all_ids = all_ids + '\t'.join(ids)

        f.write('case_list_ids: {}\n'.format(all_ids))
        f.flush()
        f.close()
