"""Process Cufflinks pipeline output"""

def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    import logging
    from constants.constants import config2name_map
    from support import helper
    from generate import meta
    from generate.analysis_pipelines.MRNA_EXPRESSION.support_functions import alpha_sort, generate_expression_matrix, generate_expression_zscore

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger

    logger.info('Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
    meta_config = helper.relocate_inputs(meta_config, study_config, verb)

    logger.info('Alpha sorting each file ...')
    alpha_sort(meta_config, verb)

    logger.info('Generating expression matrix ...')
    generate_expression_matrix(meta_config, study_config, verb)

    logger.info('Generating expression Meta ...')
    meta.generate_meta_type(meta_config,study_config,logger)

    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores']:
        logger.info('Generating expression Z-Score Data ...')
        generate_expression_zscore(
            meta_config,
            os.path.join(study_config.config_map['output_folder'],
                         'data_{}.txt'.format(config2name_map[meta_config.alterationtype+":"+meta_config.datahandler])),
            study_config.config_map['output_folder'],
            False,
            False,
            verb
        )
        logger.info('Generating expression Z-Score Meta ...')
        # Tweak the config to write zscore metadata; TODO do this more transparently
        meta_config.datahandler = 'Z-SCORE'
        meta.generate_meta_type(meta_config, study_config, logger)


if __name__ == '__main__':
    main()
