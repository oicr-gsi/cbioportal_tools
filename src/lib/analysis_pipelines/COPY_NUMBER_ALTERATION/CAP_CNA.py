from lib.support import helper
from lib.analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import fix_chrom, fix_seg_id, preProcCNA

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
    #subprocess.call(['/usr/bin/Rscript', '--vanilla', '/.mounts/labs/gsiprojects/gsi/cBioGSI/aliang/cbioportal_tools/src/lib/analysis_pipelines/COPY_NUMBER_ALTERATION/preProcCNA.r'])
    preProcCNA(meta_config, study_config, meta_config.config_map['genebed'], meta_config.config_map['genelist'], meta_config.config_map['gain'], meta_config.config_map['ampl'], meta_config.config_map['htzd'], meta_config.config_map['hmzd'])

if __name__ == '__main__':
    main()
