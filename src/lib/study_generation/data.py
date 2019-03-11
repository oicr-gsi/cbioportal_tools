import os

import numpy as np

import lib.support.helper
from lib.constants import config2name_map
from lib.data_type import mutation_data, segmented_data, cancer_type
from lib.support import Config, helper


def generate_data_type(meta_config: Config.Config, study_config: Config.Config, force, verb):

    if meta_config.type_config == 'MAF':
        helper.working_on(verb, message='Gathering and decompressing mutation files into temporary folder...')
        lib.support.helper.decompress_to_temp(meta_config, study_config, verb)
        helper.working_on(verb)

        convert_vcf_2_maf = True

        # If the caller contains .maf inside or does not exist, do not do conversion
        try:
            if '.maf' in meta_config.config_map['caller']:
                convert_vcf_2_maf = False
            elif meta_config.config_map['caller'] == 'Strelka':
                # Do some pre-processing
                print('Something should be done')
            elif meta_config.config_map['caller'] == 'Mutect':
                mutation_data.filter_vcf(meta_config, verb)

            elif meta_config.config_map['caller'] == 'Mutect2':
                mutation_data.filter_vcf(meta_config, verb)

            elif meta_config.config_map['caller'] == 'MutectStrelka':
                mutation_data.filter_vcf(meta_config, verb)

            elif meta_config.config_map['caller'] == 'GATKHaplotypeCaller':
                # Do some other sort of pre-processing
                print('Something else should be done')
            else:
                helper.stars()
                print('WARNING:: Unknown caller, have you spelled it right?')
                print('See: {}'.format(mutation_data.mutation_callers))
                helper.stars()
        except KeyError:
            convert_vcf_2_maf = False

        if convert_vcf_2_maf:
            helper.working_on(verb, message='Exporting vcf2maf...')
            helper.working_on(verb, message='And deleting .vcf s...')
            meta_config = mutation_data.export2maf(meta_config, study_config, force, verb)
            helper.working_on(verb)

        helper.working_on(verb, message='Generating wanted_columns.txt file for cBioWrap...')
        mutation_data.wanted_columns(meta_config, study_config)
        helper.working_on(verb)

        helper.working_on(verb, message='Re-zipping .mafs for cBioWrap ...')
        meta_config = mutation_data.zip_maf_files(meta_config, force)
        helper.working_on(verb)

    elif meta_config.type_config == 'SEG':
        helper.working_on(verb, message='Gathering and decompressing SEG files into temporary folder')
        lib.support.helper.decompress_to_temp(meta_config, study_config, verb)
        helper.working_on(verb)

        helper.working_on(verb, 'Caller is {}, beginning pre-processing...'.format(meta_config.config_map['pipeline']))

        if meta_config.config_map['pipeline'] == 'CNVkit':
            # Do some pre-processing
            print('Seems nothing should be done')

        elif meta_config.config_map['pipeline'] == 'Sequenza':

            segmented_data.fix_sequenza_chrom(meta_config, study_config, verb)

    elif meta_config.type_config == 'CANCER_TYPE':
        helper.working_on(verb, message='Reading colours...')
        colours = cancer_type.get_colours()
        helper.working_on(verb)

        helper.working_on(verb, message='Generating CANCER_TYPE records...')
        cancer_type.gen_cancer_type_data(meta_config, study_config, colours)
        helper.working_on(verb)


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