__author__ = ["Kunal Chandan", "Lawrence Heisler"]
__email__ = ["kchandan@uwaterloo.ca", "Lawrence.Heisler@oicr.on.ca"]
__version__ = "1.0"
__status__ = "Production"

import os
import typing
import pandas as pd
import numpy as np

from lib.support import Config, helper
from lib.constants.constants import config2name_map

DataFrames = typing.List[pd.DataFrame]


def alpha_sort(exports_config: Config.Config, verb):
    input_folder = exports_config.config_map['input_folder']
    calls = []

    for each in exports_config.data_frame['FILE_NAME']:
        output_file = os.path.join(input_folder, each)

        calls.append(helper.parallel_call('head -n +1 {0} >  {0}.temp;'
                                          'tail -n +2 {0} | sort >> {0}.temp;'
                                          'mv {0}.temp {0}'.format(output_file), verb))

    # Wait until Baked
    exit_codes = [p.wait() for p in calls]

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Cufflinks format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def generate_expression_matrix(exports_config: Config.Config, study_config: Config.Config, verb):
    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.alterationtype + ":" + exports_config.datatype]))

    helper.working_on(verb, message='Reading FPKM data ...')
    info: DataFrames = []
    for i in range(exports_config.data_frame.shape[0]):
        info.append(pd.read_csv(os.path.join(exports_config.config_map['input_folder'],
                                             exports_config.data_frame['FILE_NAME'][i]),
                                sep='\t',
                                usecols=['gene_id','FPKM'])
                    .rename(columns={'FPKM': exports_config.data_frame['SAMPLE_ID'][i],
                                     'gene_id': 'Hugo_Symbol'})
                    .drop_duplicates(subset='Hugo_Symbol', keep='last', inplace=False))

    helper.working_on(verb, message='Merging all FPKM data ...')
    if len(info) == 0:
        raise ImportError('Attempting to import zero expression data, please remove expression data from study.')
    elif len(info) == 1:
        result = info[0]
    else:
        result = info[0]
        for i in range(1, len(info)):
            result: pd.DataFrame = pd.merge(result, info[i], how='outer', on='Hugo_Symbol')
            result.drop_duplicates(subset='Hugo_Symbol', keep='last', inplace=True)
    result.replace(np.nan, 0, inplace=True)

    helper.working_on(verb, message='Writing all FPKM data ...')
    result.to_csv(output_file, sep='\t', index=None)


def generate_expression_zscore(exports_config: Config.Config, study_config: Config.Config, verb):
    input_file = os.path.join(study_config.config_map['output_folder'],
                              'data_{}.txt'.format(config2name_map[exports_config.alterationtype + ":" + exports_config.datatype]))

    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.alterationtype + ":Z-SCORE"]))

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
