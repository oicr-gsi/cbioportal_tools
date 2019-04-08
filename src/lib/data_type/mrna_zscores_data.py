import os

import pandas as pd

from lib.constants.constants import config2name_map
from lib.support import Config, helper


def generate_expression_zscore(exports_config: Config.Config, study_config: Config.Config, verb):
    input_file = os.path.join(study_config.config_map['output_folder'],
                              'data_{}.txt'.format(config2name_map['MRNA_EXPRESSION']))

    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.type_config]))

    # Z-Scores written by Dr. L Heisler
    helper.working_on(verb, message='Reading FPKM Matrix ...')
    raw_data = pd.read_csv(input_file, sep='\t')

    helper.working_on(verb, message='Processing FPKM Matrix ...')
    raw_scores = raw_data.drop(['Hugo_Symbol'], axis=1)
    means = raw_scores.mean(axis=1)
    sds = raw_scores.std(axis=1)

    z_scores = ((raw_scores.transpose() - means) / sds).transpose()
    z_scores = z_scores.fillna(0)
    z_scores = z_scores.round(decimals=4)
    z_scores_data = pd.concat([raw_data['Hugo_Symbol'], z_scores], axis=1)

    helper.working_on(verb, message='Writing FPKM Z-Scores Matrix ...')
    z_scores_data.to_csv(output_file, sep="\t", index=False)