from lib.support import helper
from lib.analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import fix_chrom, fix_seg_id

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


if __name__ == '__main__':
    main()