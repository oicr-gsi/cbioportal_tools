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
    helper.call_shell('Rscript {}'
                      '-s {} '
                      '-g {} '
                      '-o {} '.format(os.path.join(janus_path, 'lib/data_type/seg2gene.R '), seg_file, bed_file, l_o_file), verb)