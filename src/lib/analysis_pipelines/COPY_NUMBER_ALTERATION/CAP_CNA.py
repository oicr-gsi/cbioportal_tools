__author__ = "Allan Liang"
__email__ = "a33liang@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

from lib.support import helper
from lib.analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import fix_chrom, fix_seg_id, preProcCNA, ProcCNA
from lib.study_generation import meta

def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing SEG files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Fixing Chromosome numbering ...')
    fix_chrom(meta_config, study_config, verb)
    helper.working_on(verb)

    
    helper.working_on(verb, message='Fixing .SEG IDs')
    fix_seg_id(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Concatenating SEG Files to export folder')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)
    
    #Call preProcCNA.r to generate reduced seg files
    helper.working_on(verb, message='Generating reduced SEG files ...')
    preProcCNA(meta_config, study_config, meta_config.config_map['genebed'], meta_config.config_map['genelist'], meta_config.config_map['gain'], meta_config.config_map['ampl'], meta_config.config_map['htzd'], meta_config.config_map['hmzd'])
    helper.working_on(verb)

    helper.working_on(verb, message='Generating CNA and log2CNA files ...')
    ProcCNA(meta_config, study_config, meta_config.config_map['genebed'], meta_config.config_map['genelist'], meta_config.config_map['gain'], meta_config.config_map['ampl'], meta_config.config_map['htzd'], meta_config.config_map['hmzd'], meta_config.config_map['oncokb_api_token'], verb)
    helper.working_on(verb)

    # Generate meta data within the handler and not in generator.py    
    helper.working_on(verb, message='Generating segments Meta ...')
    meta.generate_meta_type(meta_config,study_config,verb)
    helper.working_on(verb)

    if 'DISCRETE' in meta_config.config_map.keys() and meta_config.config_map['DISCRETE'].lower() == 'true':
        helper.working_on(verb, message='Generating DISCRETE Meta ...')
        meta_config.datahandler = 'DISCRETE'
        meta.generate_meta_type(meta_config,study_config,verb)
        helper.working_on(verb)

    if 'CONTINUOUS' in meta_config.config_map.keys() and meta_config.config_map['CONTINUOUS'].lower() == 'true':
        helper.working_on(verb, message='Generating CONTINUOUS Meta ...')
        meta_config.datahandler = 'CONTINUOUS'
        meta.generate_meta_type(meta_config,study_config,verb)
        helper.working_on(verb)

if __name__ == '__main__':
    main()
