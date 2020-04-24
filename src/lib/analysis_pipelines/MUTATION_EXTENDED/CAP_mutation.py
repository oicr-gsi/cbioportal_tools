__author__ = "Allan Liang"
__email__ = "a33liang@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

from lib.support import helper
from lib.analysis_pipelines.MUTATION_EXTENDED import support_functions
from lib.study_generation import meta


def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    # Decompress MAF files to temp folder
    helper.working_on(verb, message='Gathering and decompressing MAF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    # Clean MAF files
    helper.working_on(verb, message='Cleaning MAF Files ...')
    support_functions.clean_head(meta_config, verb)
    helper.working_on(verb)

    # Concatenate MAF files
    helper.working_on(verb, message='Concating MAF Files to export folder  ...')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)

    # Genearte the meta data files for mutation extended data
    helper.working_on(verb, message='Generating MUTATION_EXTENDED Meta ...')
    meta.generate_meta_type(meta_config,study_config,verb)
    helper.working_on(verb)
    
    #Filtering MAF Files
    helper.working_on(verb, message='Filtering MAF Files ...')
    support_functions.maf_filter(meta_config, study_config, meta_config.config_map['Mutation_Type'], meta_config.config_map['Filter_Exception'], meta_config.config_map['Minimum_Tumour_Depth'], meta_config.config_map['Minimum_Tumour_AF'], meta_config.config_map['Maximum_gnomAD_AF'], meta_config.config_map['Maximum_Local_Freq'])
    helper.working_on(verb)

    #oncokb-annotation
    helper.working_on(verb, message='Annotating MAF files ...')
    support_functions.oncokb_annotation(meta_config, study_config, meta_config.config_map['oncokb_api_token'], verb)
    helper.working_on(verb)

    #TGL Pipe Filtering
    helper.working_on(verb, message='Filtering TGL pipe ...')
    support_functions.TGL_filter(meta_config, study_config)
    helper.working_on(verb)

if __name__ == '__main__':
    main()
