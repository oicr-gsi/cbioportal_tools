from support import helper
from analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import fix_hmmcopy_tsv, fix_chrom, fix_hmmcopy_max_chrom, fix_seg_id

def main():
    global meta_config
    global study_config
    global janus_path
    global verb


    helper.working_on(verb, message='Gathering and decompressing SEG files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Fixing HMMCopy formatting, chromosome, and chromosome max-length ...')
    fix_hmmcopy_tsv(meta_config, study_config, verb)
    fix_chrom(meta_config, study_config, verb)

    ### fix_hmmcopy_max_chrom fixes the maximum chromosome length AND imputes the num.mark value
    fix_hmmcopy_max_chrom(meta_config, study_config, janus_path, verb)

    helper.working_on(verb)

    helper.working_on(verb, message='Fixing .SEG IDs')
    fix_seg_id(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Concating SEG Files to export folder')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)


if __name__ == '__main__':
    main()
