"""Support for CAP mRNA expression data"""


def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    # imports are moved into the main (and only) method to work with the legacy component class
    import logging
    import os
    from support import helper
    from generate import meta
    from generate.analysis_pipelines.MRNA_EXPRESSION.support_functions import alpha_sort, generate_expression_matrix, generate_expression_percentile, generate_expression_zscore, preProcRNA
    from constants.constants import config2name_map

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger

    logger.info('Started processing data for CAP_expression pipeline')
    
    logger.info('Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)

    logger.info('Alpha sorting each file ...')
    alpha_sort(meta_config, verb)

    logger.info('Generating expression matrix ...')
    generate_expression_matrix(meta_config, study_config, verb)

    #preProcRNA - generate processed continuous data using the generated expression matrix - one for study and one for study comparison and one for TCGA data
    preProcRNA(meta_config, study_config, '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], True, False)
    preProcRNA(meta_config, study_config, '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), meta_config.config_map['enscon'], meta_config.config_map['genelist'], False, True)

    if meta_config.config_map.get('zscores'):
        # Generate the z-scores for mRNA expression data
        logger.info('Generating expression Z-Score Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , False, False, verb)

        # Generate the mRNA expression percentile data
        logger.info('Generating expression Percentile Data ...')
        generate_expression_percentile(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE'])),
            study_config.config_map['output_folder']
            , False, False, verb)

        # Generate the z-score sfor mRNA expression comparison data
        logger.info('Generating expression Z-Score comparison Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , True, False, verb)

        # Generate the mRNA expression comparison percentile data
        logger.info('Generating expression Percentile comparison Data ...')
        generate_expression_percentile(meta_config, os.path.join(study_config.config_map['output_folder'], 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE'])),
            study_config.config_map['output_folder']
            , True, False, verb)

        # Generate the z-scores for mRNA expression TCGA data
        helper.working_on(verb, message='Generating expression TCGA Z-Score Data ...')
        generate_expression_zscore(meta_config, os.path.join(study_config.config_map['output_folder'],
            'data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])),
            study_config.config_map['output_folder']
            , False, True, verb)

        # Generate the TCGA mRNA expression percentile data
        logger.info('Generating expression TCGA Percentile Data ...')
        generate_expression_percentile(meta_config, os.path.join(study_config.config_map['output_folder'], 'supplementary_data', 
            'data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE'])),
            study_config.config_map['output_folder']
            , False, True, verb)

    # Generate meta data within the handler and not in generator.py
    # Generate metadata for mRNA expression continuous data
    logger.info('Generating expression Meta ...')
    meta.generate_meta_type(meta_config,study_config,logger)
    
    # Generate metadata for mRNA expression z-score data
    if meta_config.config_map.get('zscores'):
        logger.info('Generating expression Z-Score Meta ...')
        meta_config.datahandler = 'Z-SCORE'
        meta.generate_meta_type(meta_config,study_config,logger)

    logger.info('Finished processing data for CAP_expression pipeline')
        
if __name__ == '__main__':

    main()
