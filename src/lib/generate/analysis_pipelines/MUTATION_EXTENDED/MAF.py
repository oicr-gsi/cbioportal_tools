"""Support for MAF files"""

# TODO this module does not appear to be used anywhere else; can it be deleted?

def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    from support import helper
    from analysis_pipelines.MUTATION_EXTENDED import support_functions

    logger.info('Gathering and decompressing MAF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)

    logger.info('Cleaning MAF Files')
    support_functions.clean_head(meta_config, verb)

    logger.info('Concatenating MAF Files to export folder')
    helper.concat_files(meta_config, study_config, verb)


if __name__ == '__main__':
    main()
