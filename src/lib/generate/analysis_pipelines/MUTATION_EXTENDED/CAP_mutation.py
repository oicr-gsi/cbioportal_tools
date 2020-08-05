"""Support for CAP mutation data"""


def main():
    global meta_config
    global study_config
    global janus_path
    global logger

    import logging
    import os
    from support import helper
    from generate import meta
    from generate.analysis_pipelines.MUTATION_EXTENDED import support_functions

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger

    logger.info('Started processing data for CAP_mutation pipeline')
    
    # Decompress MAF files to temp folder
    logger.info('Gathering and decompressing MAF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)

    # Clean MAF files
    logger.info('Cleaning MAF Files ...')
    support_functions.clean_head(meta_config, verb)

    # Concatenate MAF files
    logger.info('Concatenating MAF Files to export folder  ...')
    helper.concat_files(meta_config, study_config, verb)

    # Generate the meta data files for mutation extended data
    logger.info('Generating MUTATION_EXTENDED Meta ...')
    meta.generate_meta_type(meta_config,study_config,logger)
    
    #Filtering MAF Files
    logger.info('Filtering MAF Files ...')
    support_functions.maf_filter(meta_config, study_config, meta_config.config_map['Mutation_Type'], meta_config.config_map['Filter_Exception'], meta_config.config_map['Minimum_Tumour_Depth'], meta_config.config_map['Minimum_Tumour_AF'], meta_config.config_map['Maximum_gnomAD_AF'], meta_config.config_map['Maximum_Local_Freq'])

    #oncokb-annotation
    logger.info('Annotating MAF files ...')
    support_functions.oncokb_annotation(meta_config, study_config, meta_config.config_map['oncokb_api_token'], verb)

    #TGL Pipe Filtering
    logger.info('Filtering TGL pipe ...')
    support_functions.TGL_filter(meta_config, study_config)

    logger.info('Finished processing data for CAP_mutation pipeline')

if __name__ == '__main__':
    main()
