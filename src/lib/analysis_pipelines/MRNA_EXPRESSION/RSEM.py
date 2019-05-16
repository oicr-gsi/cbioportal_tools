from lib.support import helper
from lib.study_generation import meta
from lib.analysis_pipelines.MRNA_EXPRESSION.support_functions import alpha_sort, generate_expression_matrix, generate_expression_zscore

def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Alpha sorting each file ...')
    alpha_sort(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Generating expression matrix ...')
    generate_expression_matrix(meta_config, study_config, verb)
    helper.working_on(verb)

    # Works because shorting ...
    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':
        helper.working_on(verb, message='Generating expression Z-Score Meta ...')
        meta.generate_meta_type(meta_config,study_config,verb)
        #meta.generate_meta_type(meta_config.alterationtype + '_ZSCORES',
        #                {'profile_name': 'mRNA expression z-scores','profile_description': 'Expression level z-scores'}, study_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Generating expression Z-Score Data ...')
        generate_expression_zscore(meta_config, study_config, verb)
        helper.working_on(verb)


if __name__ == '__main__':
    main()
