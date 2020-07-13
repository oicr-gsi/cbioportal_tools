from support import helper
from study_generation import meta
from data_type.MRNA_EXPRESSION import mrna_data, mrna_zscores_data
from analysis_pipelines.MRN_EXPRESSION.support_functions import fix_chrom, fix_seg_id

def main():
    global meta_config
    global study_config
    global janus_path
    global verb

    helper.working_on(verb, message='Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
    helper.decompress_to_temp(meta_config, study_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Alpha sorting each file ...')
    mrna_data.alpha_sort(meta_config, verb)
    helper.working_on(verb)

    helper.working_on(verb, message='Generating expression matrix ...')
    mrna_data.generate_expression_matrix(meta_config, study_config, verb)
    helper.working_on(verb)

    # Works because shorting ...
    if 'zscores' in meta_config.config_map.keys() and meta_config.config_map['zscores'].lower() == 'true':
        helper.working_on(verb, message='Generating expression Z-Score Meta ...')
        meta.generate_meta_type(meta_config.type_config + '_ZSCORES',
                                {'profile_name': 'mRNA expression z-scores',
                                 'profile_description': 'Expression level z-scores'}, study_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Generating expression Z-Score Data ...')
        mrna_zscores_data.generate_expression_zscore(meta_config, study_config, verb)
        helper.working_on(verb)


if __name__ == '__main__':
    main()