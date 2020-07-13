from support import helper
from analysis_pipelines.COPY_NUMBER_ALTERATION.support_functions import discrete_copy_number_data

def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Generating CNA files ...')
    discrete_copy_number_data.gen_dcna(meta_config, study_config, verb)
    helper.working_on(verb)

if __name__ == '__main__':
    main()