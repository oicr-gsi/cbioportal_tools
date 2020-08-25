"""Process Cufflinks pipeline output"""

def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    import logging
    from support import helper
    from generate import meta
    from analysis_pipelines.MRNA_EXPRESSION.support_functions import alpha_sort, fix_chrom, fix_seg_id, generate_expression_matrix, generate_expression_zscore

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger

    logger.info('Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
    meta_config = helper.relocate_inputs(meta_config, study_config, verb)

    logger.info('Alpha sorting each file ...')
    alpha_sort(meta_config, verb)

    logger.info('Generating expression matrix ...')
    generate_expression_matrix(meta_config, study_config, verb)

    # Works because shorting ...
    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores']:
        logger.info('Generating expression Z-Score Meta ...')
        meta.generate_meta_type(
            meta_config.type_config + '_ZSCORES',
            {
                'profile_name': 'mRNA expression z-scores',
                'profile_description': 'Expression level z-scores'
            },
            study_config,
            logger
        )
        logger.info('Generating expression Z-Score Data ...')
        generate_expression_zscore(meta_config, study_config, verb)


if __name__ == '__main__':
    main()
