from lib.support import helper
from lib.data_type.SEG import segmented_data


def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing SEG files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Fixing Chromosome numbering ...')
    segmented_data.fix_chrom(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Fixing .SEG IDs')
    segmented_data.fix_seg_id(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Concating SEG Files to export folder')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)


if __name__ == '__main__':
    main()