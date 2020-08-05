"""MutectStrelka pipeline support"""


def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    import logging
    from support import helper
    from generate.analysis_pipelines.MUTATION_EXTENDED import support_functions

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger

    logger.info('Gathering and decompressing VCF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)

    logger.info('Ensuring both columns exist, otherwise adding UNMATCHED column ...')
    support_functions.verify_dual_columns(meta_config, verb)

    logger.info('Filtering for only PASS ...')
    support_functions.filter_vcf_rejects(meta_config, verb)

    logger.info('Exporting vcf2maf...')
    logger.info('And deleting .vcf s...')
    meta_config = support_functions.export2maf(meta_config, study_config, verb)

    # Generate the meta data files for mutation extended data
    logger.info('Generating MUTATION_EXTENDED Meta ...')
    meta.generate_meta_type(meta_config,study_config,logger)
    
    logger.info('Cleaning MAF Files ...')
    support_functions.clean_head(meta_config, verb)

    logger.info('Concating MAF Files to export folder  ...')
    helper.concat_files(meta_config, study_config, verb)

    logger.info('Finished processing data for MutectStrelka pipeline')


if __name__ == '__main__':
    main()
