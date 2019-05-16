from lib.support import helper
from lib.data_type.CONTINUOUS_COPY_NUMBER import continuous_copy_number_data


def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Generating log2CNA files ...')
    continuous_copy_number_data.gen_log2cna(meta_config, study_config, janus_path, verb)
    helper.working_on(verb)


if __name__ == '__main__':
    main()