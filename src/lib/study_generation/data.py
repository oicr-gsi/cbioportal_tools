__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os

import numpy as np

from lib.constants import config2name_map
from lib.data_type import mutation_data, segmented_data, mrna_data, cancer_type
from lib.support import Config, helper


def generate_data_type(meta_config: Config.Config, study_config: Config.Config, force, verb):

    if   meta_config.type_config == 'MAF':

        helper.working_on(verb, message='Gathering and decompressing mutation files into temporary folder...')
        helper.decompress_to_temp(meta_config, study_config, verb)
        helper.working_on(verb)

        convert_vcf_2_maf = True

        # If the caller contains .maf inside or does not exist, do not do conversion
        # Since the caller option in the meta file is optional, try:
        try:
            if '.maf' in meta_config.config_map['caller']:
                convert_vcf_2_maf = False
        except KeyError:
            convert_vcf_2_maf = False

        if convert_vcf_2_maf:
            if   meta_config.config_map['caller'] == 'Strelka':

                print('Something should be done')

            elif meta_config.config_map['caller'] == 'Mutect':

                mutation_data.filter_vcf(meta_config, verb)

            elif meta_config.config_map['caller'] == 'Mutect2':

                mutation_data.filter_vcf(meta_config, verb)

            elif meta_config.config_map['caller'] == 'MutectStrelka':

                mutation_data.filter_vcf(meta_config, verb)

            elif meta_config.config_map['caller'] == 'GATKHaplotypeCaller':

                print('Something else should be done')
                # Any expansion for pre-processing the .vcf Files should be put here in an 'elif'.
            else:
                helper.stars()
                print('WARNING:: Unknown caller, have you spelled it right?')
                print('See: {}'.format(mutation_data.mutation_callers))
                helper.stars()

            helper.working_on(verb, message='Exporting vcf2maf...')
            helper.working_on(verb, message='And deleting .vcf s...')
            meta_config = mutation_data.export2maf(meta_config, study_config, force, verb)
            helper.working_on(verb)

        helper.working_on(verb, message='Cleaning MAF Files ...')
        mutation_data.clean_head(meta_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Concating MAF Files to export folder  ...')
        helper.concat_files(meta_config, study_config, verb)
        helper.working_on(verb)

    elif meta_config.type_config == 'SEG':

        helper.working_on(verb, message='Gathering and decompressing SEG files into temporary folder')
        helper.decompress_to_temp(meta_config, study_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, 'Caller is {}, beginning pre-processing...'.format(meta_config.config_map['pipeline']))
        if   meta_config.config_map['pipeline'] == 'CNVkit':

            print('Seems no prep is needed for CNVkit')

        elif meta_config.config_map['pipeline'] == 'Sequenza':
            # It might be that this is not necessary
            segmented_data.fix_chrom(meta_config, study_config, verb)

        elif meta_config.config_map['pipeline'] == 'HMMCopy':

            segmented_data.fix_hmmcopy_tsv(meta_config, study_config, verb)
            segmented_data.fix_chrom(meta_config, study_config, verb)
            segmented_data.fix_hmmcopy_max_chrom(meta_config, study_config, verb)

        helper.working_on(verb, message='Fixing .SEG IDs')
        segmented_data.fix_seg_id(meta_config, study_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Concating SEG Files to export folder')
        helper.concat_files(meta_config, study_config, verb)
        helper.working_on(verb)

    elif meta_config.type_config == 'MRNA_EXPRESSION':

        helper.working_on(verb, message='Gathering and decompressing MRNA_EXPRESSION files into temporary folder')
        helper.decompress_to_temp(meta_config, study_config, verb)
        helper.working_on(verb)

        if   meta_config.config_map['pipeline'] == 'Cufflinks':
            mrna_data.cufflinks_prep(meta_config, study_config, verb)

        helper.working_on(verb, message='Alpha sorting each file ...')
        mrna_data.alpha_sort(meta_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Generating expression matrix ...')
        mrna_data.generate_expression_matrix(meta_config, study_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, message='Generating expression Z-Score Data ...')
        mrna_data.generate_expression_zscore(meta_config, study_config, verb)
        helper.working_on(verb)
        # TODO:: Generate z-zscore data.

    elif meta_config.type_config == 'CANCER_TYPE':
        helper.working_on(verb, message='Reading colours...')
        colours = cancer_type.get_colours()
        helper.working_on(verb)

        helper.working_on(verb, message='Generating CANCER_TYPE records...')
        cancer_type.gen_cancer_type_data(meta_config, study_config, colours)
        helper.working_on(verb)

    else:
        raise TypeError('ERROR:: A specified config file does not have a supported type_config attribute. \n' +
                        'See these: [ {} ]'.format(' | '.join(config2name_map.keys())))


def generate_data_clinical(samples_config: Config.ClinicalConfig, study_config: Config.Config, verb):
    num_header_lines = 4

    helper.working_on(verb, message='Writing to data_{}.txt ...'.format(config2name_map[samples_config.type_config]))

    output_file = os.path.join(os.path.abspath(study_config.config_map['output_folder']),
                               'data_{}.txt'.format(config2name_map[samples_config.type_config]))

    array = np.array(samples_config.data_frame)

    f = open(output_file, 'w')
    for i in range(array.shape[0]):
        if i < num_header_lines:
            f.write('#{}\n'.format('\t'.join(samples_config.data_frame[i])))
        else:
            f.write('{}\n'.format('\t'.join(samples_config.data_frame[i])))
    f.close()
    helper.working_on(verb)