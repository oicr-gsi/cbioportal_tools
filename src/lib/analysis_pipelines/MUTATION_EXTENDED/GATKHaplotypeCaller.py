from lib.support import helper
from lib.analysis_pipelines.MUTATION_EXTENDED import support_functions


def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing VCF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on('Ensuring both columns exist, otherwise adding UNMATCHED column ...')
    support_functions.verify_dual_columns(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Exporting vcf2maf...')
    helper.working_on(verb, message='And deleting .vcf s...')
    meta_config = support_functions.export2maf(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Cleaning MAF Files ...')
    support_functions.clean_head(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Concating MAF Files to export folder  ...')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)


if __name__ == '__main__':
    main()
