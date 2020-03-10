from lib.support import helper
from lib.analysis_pipelines.MUTATION_EXTENDED import support_functions


def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing MAF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Cleaning MAF Files ...')
    support_functions.clean_head(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Concating MAF Files to export folder  ...')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)
    
    #Filtering MAF Files
    support_functions.maf_filter(meta_config, study_config, meta_config.config_map['Mutation_Type'], meta_config.config_map['Filter_Exception'], meta_config.config_map['Minimum_Tumour_Depth'], meta_config.config_map['Minimum_Tumour_AF'], meta_config.config_map['Maximum_gnomAD_AF'], meta_config.config_map['Maximum_Local_Freq'])

    #oncokb-annotation
    support_functions.oncokb_annotation(meta_config, study_config, meta_config.config_map['oncokb_api_token'], verb)

    #TGL Pipe Filtering
    support_functions.TGL_filter(meta_config, study_config)

if __name__ == '__main__':
    main()
