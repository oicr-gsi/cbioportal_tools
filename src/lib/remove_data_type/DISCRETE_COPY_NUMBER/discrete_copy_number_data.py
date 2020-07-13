"""Remove discrete copy number data"""

import os

import pandas as pd

from constants import constants
from support import Config, helper

thresholds:list  = []

def collapse(num):
    [hmzd, htzd, gain, ampl] = thresholds

    if num > ampl:
        return +2

    elif num > gain:
        return +1

    elif num > htzd:
        return +0

    elif num > hmzd:
        return -1

    else:
        return -2


def gen_dcna(exports_config: Config.Config, study_config: Config.Config, verb):

    # This is dCNA
    # Requires cCNA to be generated already
    helper.working_on(verb, message='Gathering files ...')
    l_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map['CONTINUOUS_COPY_NUMBER']))
    c_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config]))
    global thresholds
    thresholds = [float(x) for x in exports_config.config_map['thresholds'].split(',')]
    if os.path.exists(l_o_file):
        helper.working_on(verb, message='Generating dCNA (CNA)...')
        data = pd.read_csv(l_o_file, sep='\t')
        cols = data.columns.values.tolist()[1:]

        # This code here had an astonishing 5500x improvement compared to traversal over it as a 2D array, and yes 5500x
        for c in cols:
            data[c] = data[c].apply(lambda x: collapse(x))

        data.to_csv(c_o_file, sep='\t', index=None)
    else:
        print('ERROR:: Cannot generate dCNA file because log2CNA file does not exist ...')
        print('ERROR:: Either remove the DISCRETE data config file, or add a CONTINUOUS data config file ')
        helper.stars()
        helper.stars()
        exit(1)


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
