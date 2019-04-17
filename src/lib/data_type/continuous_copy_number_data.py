__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os

from lib.constants import constants
from lib.support import Config, helper


def gen_log2cna(exports_config: Config.Config, study_config: Config.Config, janus_path, verb):

    # This is log2CNA
    helper.working_on(verb, message='Gathering files ...')
    seg_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map['SEG']))
    bed_file = exports_config.config_map['bed_file']
    l_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config]))

    helper.working_on(verb, message='Generating log2CNA...')

    # This may break if after loading the module R-gsi/3.5.1, Rscript is not set as a constant
    helper.call_shell('Rscript {} '
                      '-s {} '
                      '-g {} '
                      '-o {} '.format(os.path.join(janus_path, constants.seg2gene), seg_file, bed_file, l_o_file), verb)


def verify_final_file(exports_config: Config.Config, verb):
    data = open(os.path.join(exports_config.config_map['input_folder'],
                            exports_config.data_frame['FILE_NAME'][0]), 'w')

    t_config = exports_config.type_config
    header = data.readline().strip().split('\t')
    minimum_header = ['Entrez_Gene_Id', 'Hugo_Symbol']

    helper.working_on(verb, message='Asserting minimum header is in {} file.'.format(t_config))
    if not any([a in header for a in minimum_header]):
        print([a if a not in header else '' for a in minimum_header])
        print('Missing header(s) from {} file have been printed above, ensure data isn\'t missing.'.format(t_config))
        exit(1)
