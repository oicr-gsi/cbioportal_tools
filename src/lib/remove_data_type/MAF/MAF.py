from support import helper
from data_type.MAF import mutation_data


def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing MAF files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Cleaning MAF Files ...')
    mutation_data.clean_head(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Concating MAF Files to export folder  ...')
    helper.concat_files(meta_config, study_config, verb)
    helper.working_on(verb)


if __name__ == '__main__':
    main()