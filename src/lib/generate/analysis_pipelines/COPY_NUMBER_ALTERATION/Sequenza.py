"""Process Sequenza data"""

def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    import logging

    from support import helper
    from generate.analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import fix_chrom, fix_seg_id

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger

    logger.info('Gathering and decompressing SEG files into temporary folder, and updating config')
    meta_config = helper.relocate_inputs(meta_config, study_config, verb)
    logger.info('Done.')

    logger.info('Fixing Chromosome numbering ...')
    fix_chrom(meta_config, study_config, logger)
    logger.info('Done.')

    logger.info('Fixing .SEG IDs')
    fix_seg_id(meta_config, study_config, logger)
    logger.info('Done.')

    logger.info('Concatenating SEG Files to export folder')
    helper.concat_files(meta_config, study_config, verb)
    logger.info('Done.')


if __name__ == '__main__':
    main()
