__author__ = "Allan Liang"
__email__ = "a33liang@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os

from lib.support import helper
from lib.study_generation import meta
from lib.analysis_pipelines.MRNA_EXPRESSION.support_functions import alpha_sort, generate_expression_matrix, generate_expression_percentile, generate_expression_zscore, preProcRNA
from lib.constants.constants import config2name_map

def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Alpha sorting each file ...')
    alpha_sort(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Generating expression matrix ...')
    generate_expression_matrix(meta_config, study_config, verb)
    helper.working_on(verb)
    
    #preProcRNA - generate processed continuous data using the generated expression matrix - one for study and one for study comparison and one for TCGA data
    preProcRNA(meta_config, study_config, '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], True, False)
    preProcRNA(meta_config, study_config, '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], False, True)

    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':
        # Generate the z-scores for mRNA expression data
        helper.working_on(verb, message='Generating expression Z-Score Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , False, False, verb)
        helper.working_on(verb)

        # Generate the mRNA expression percentile data
        helper.working_on(verb, message='Generating expression Percentile Data ...')
        generate_expression_percentile(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE'])),
            study_config.config_map['output_folder']
            , False, False, verb)
        helper.working_on(verb)

        # Generate the z-score sfor mRNA expression comparison data
        helper.working_on(verb, message='Generating expression Z-Score comparison Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , True, False, verb)
        helper.working_on(verb)

        # Generate the mRNA expression comparison percentile data
        helper.working_on(verb, message='Generating expression Percentile comparison Data ...')
        generate_expression_percentile(meta_config, os.path.join(study_config.config_map['output_folder'], 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE'])),
            study_config.config_map['output_folder']
            , True, False, verb)
        helper.working_on(verb)

        # Generate the z-scores for mRNA expression TCGA data
        helper.working_on(verb, message='Generating expression TCGA Z-Score Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , False, True, verb)
        helper.working_on(verb)

        # Generate the TCGA mRNA expression percentile data
        helper.working_on(verb, message='Generating expression TCGA Percentile Data ...')
        generate_expression_percentile(meta_config, os.path.join(study_config.config_map['output_folder'], 'supplementary_data', 
            'data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE'])),
            study_config.config_map['output_folder']
            , False, True, verb)
        helper.working_on(verb)

    # Generate meta data within the handler and not in generator.py
    # Generate metadata for mRNA expression continuous data
    helper.working_on(verb, message='Generating expression Meta ...')
    meta.generate_meta_type(meta_config,study_config,verb)
    helper.working_on(verb)
    
    # Generate metadata for mRNA expression z-score data
    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':
        helper.working_on(verb, message='Generating expression Z-Score Meta ...')
        meta_config.datahandler = 'Z-SCORE'
        meta.generate_meta_type(meta_config,study_config,verb)
        helper.working_on(verb)

if __name__ == '__main__':
    main()
