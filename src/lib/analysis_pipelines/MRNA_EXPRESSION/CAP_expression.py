import os

from lib.support import helper
from lib.study_generation import meta
from lib.analysis_pipelines.MRNA_EXPRESSION.support_functions import alpha_sort, generate_expression_matrix, generate_expression_zscore, preProcRNA, generate_TCGA_data
#TEST#
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

    # Works because shorting ...
    #if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':
    #    helper.working_on(verb, message='Generating expression Z-Score Meta ...')
    #    meta.generate_meta_type(meta_config,study_config,verb)
    #    #meta.generate_meta_type(meta_config.alterationtype + '_ZSCORES',
    #    #                {'profile_name': 'mRNA expression z-scores','profile_description': 'Expression level z-scores'}, study_config, verb)
    #    helper.working_on(verb)

    #    helper.working_on(verb, message='Generating expression Z-Score Data ...')
    #    generate_expression_zscore(os.path.join(study_config.config_map['output_folder'],
    #        'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])), 
    #        os.path.join(study_config.config_map['output_folder'], 
    #            'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":Z-SCORE"]))
    #        , verb)
    #    helper.working_on(verb)

    #TODO REMOVE get_metadata
    #get meta_expression.txt and meta_expression_zscores.txt
    #get_metadata(meta_config, study_config)
    
    # change the gepcomp list
    #convertList(meta_config.config_map['gepfile'])    
    
    #preProcRNA
    preProcRNA(meta_config, study_config, '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], True)
    preProcRNA(meta_config, study_config, '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], False)
    #preProcRNA(meta_config, study_config, '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], True)

    # Works because shorting ...
    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':

        
        #####################meta.generate_meta_type(meta_config,study_config,verb)
        #####################meta.generate_meta_type(meta_config.alterationtype + '_ZSCORES',
        ##################                {'profile_name': 'mRNA expression z-scores','profile_description': 'Expression level z-scores'}, study_config, verb)
        ###################helper.working_on(verb)


        helper.working_on(verb, message='Generating expression Z-Score Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , False, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Generating expression Z-Score Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , True, verb)
        helper.working_on(verb)

    #preProcRNA(meta_config, study_config, meta_config.config_map['enscon'], meta_config.config_map['genelist'], meta_config.config_map['gepcomp', meta_config.config_map['gepfile']])
    
    #generate_expression_zscore(os.path.join(study_config.config_map['output_folder'],
    #    'data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ':' + meta_config.datahandler])),
    #        os.path.join(study_config.config_map['output_folder'],
    #            'new_{}.txt'.format(config2name_map[meta_config.alterationtype + ":Z-SCORE"]))
    #        , verb)

    generate_TCGA_data(meta_config, study_config)

    #TODO include all the meta data and case list generation calls into the CAP handler instead of the generator
    # Generate meta data within the handler and not in generator.py
    helper.working_on(verb, message='Generating expression Meta ...')
    meta.generate_meta_type(meta_config,study_config,verb)
    helper.working_on(verb)
    
    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':
        helper.working_on(verb, message='Generating expression Z-Score Meta ...')
        meta_config.datahandler = 'Z-SCORE'
        meta.generate_meta_type(meta_config,study_config,verb)
        helper.working_on(verb)

if __name__ == '__main__':
    main()
