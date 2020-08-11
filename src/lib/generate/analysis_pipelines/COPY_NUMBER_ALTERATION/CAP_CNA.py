"""Support for CAP CNA data"""

def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    import logging
    from support import helper
    from generate.analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import fix_chrom, fix_seg_id, preProcCNA, ProcCNA
    from generate import meta

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger
    
    logger.info('Gathering and decompressing SEG files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    logger.info('Done.')

    logger.info('Fixing Chromosome numbering ...')
    fix_chrom(meta_config, study_config, verb)
    logger.info('Done.')
    
    logger.info('Fixing .SEG IDs')
    fix_seg_id(meta_config, study_config, verb)
    logger.info('Done.')

    logger.info('Concatenating SEG Files to export folder')
    helper.concat_files(meta_config, study_config, verb)
    logger.info('Done.')
    
    #Call preProcCNA.r to generate reduced seg files
    logger.info('Generating reduced SEG files ...')
    preProcCNA(meta_config, study_config, meta_config.config_map['genebed'], meta_config.config_map['genelist'], meta_config.config_map['gain'], meta_config.config_map['ampl'], meta_config.config_map['htzd'], meta_config.config_map['hmzd'], logger)
    logger.info('Done.')

    logger.info('Generating CNA and log2CNA files ...')
    ProcCNA(meta_config, study_config, meta_config.config_map['genebed'], meta_config.config_map['genelist'], meta_config.config_map['gain'], meta_config.config_map['ampl'], meta_config.config_map['htzd'], meta_config.config_map['hmzd'], meta_config.config_map['oncokb_api_token'], verb)
    logger.info('Done.')

    # Generate meta data within the handler and not in generator.py    
    logger.info('Generating segments Meta ...')
    meta.generate_meta_type(meta_config,study_config,logger)
    logger.info('Done.')

    if 'DISCRETE' in meta_config.config_map.keys() and meta_config.config_map['DISCRETE'].lower() == 'true':
        logger.info('Generating DISCRETE Meta ...')
        meta_config.datahandler = 'DISCRETE'
        meta.generate_meta_type(meta_config,study_config,verb)
        logger.info('Done.')

    if 'CONTINUOUS' in meta_config.config_map.keys() and meta_config.config_map['CONTINUOUS'].lower() == 'true':
        logger.info('Generating CONTINUOUS Meta ...')
        meta_config.datahandler = 'CONTINUOUS'
        meta.generate_meta_type(meta_config,study_config,verb)
        logger.info('Done.')

if __name__ == '__main__':
    main()
