__author__ = ["Kunal Chandan", "Lawrence Heisler"]
__email__ = ["kchandan@uwaterloo.ca", "Lawrence.Heisler@oicr.on.ca"]
__status__ = "Pre-Production"

import os
import typing
import pandas as pd
import numpy as np

from lib.support import Config, helper
from lib.constants.constants import config2name_map

Information = typing.List[pd.DataFrame]


def cufflinks_prep(exports_config: Config.Config, study_config: Config.Config, verb):

    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    expression_folder = helper.get_temp_folder(output_folder, 'mrna_expression')
    helper.call_shell('head {}'.format(os.path.join(input_folder, export_data['FILE_NAME'][0])), verb)

    header = 'gene_id\\ttranscript_id(s)\\tlength\\teffective_length\\texpected_count\\tTPM\\tFPKM'
    # Cook
    for i in range(len(export_data)):

        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(expression_folder, export_data['FILE_NAME'][i])

        output_temp = output_file + '.temp'

        calls.append(helper.parallel_call("echo \"{}\" > {}; "
                                          "awk -F'\\t' '{{ OFS=FS }} NR>1 {{ "
                                          "temp=$10; $10=$7; $7=temp; {{ "
                                          "for(i = 8; i <= NF; i++) $i=\"\"; print }} }}' {} "
                                          ">> {};".format(header, output_temp, input_file, output_temp) +
                                          'sed \'s/[[:blank:]]*$//\' {} > {}'.format(output_temp, output_file), verb))

    exports_config.config_map['input_folder'] = expression_folder
    input_folder = exports_config.config_map['input_folder']

    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    helper.call_shell('head {}'.format(os.path.join(input_folder, export_data['FILE_NAME'][0])), verb)

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Cufflinks format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def alpha_sort(exports_config: Config.Config, verb):
    input_folder = exports_config.config_map['input_folder']
    calls = []
    helper.call_shell('head {}'.format(os.path.join(input_folder, exports_config.data_frame['FILE_NAME'][0])), verb)

    for each in exports_config.data_frame['FILE_NAME']:
        output_file = os.path.join(input_folder, each)

        calls.append(helper.parallel_call('head -n +1 {0} >  {0}.temp;'
                                          'tail -n +2 {0} | sort >> {0}.temp;'
                                          'mv {0}.temp {0}'.format(output_file), verb))

    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    helper.call_shell('head {}'.format(os.path.join(input_folder, exports_config.data_frame['FILE_NAME'][0])), verb)

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Cufflinks format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def generate_expression_matrix(exports_config: Config.Config, study_config: Config.Config, verb):
    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.type_config]))

    helper.working_on(verb, message='Reading FPKM data ...')
    info: Information = []
    for i in range(exports_config.data_frame.shape[0]):
        info.append(pd.read_csv(os.path.join(exports_config.config_map['input_folder'],
                                             exports_config.data_frame['FILE_NAME'][i]),
                                sep='\t',
                                usecols=['gene_id',
                                         'FPKM']).rename(columns={'FPKM': exports_config.data_frame['SAMPLE_ID'][i],
                                                                  'gene_id': 'Hugo_Symbol'}))

    helper.working_on(verb, message='Merging all FPKM data ...')
    if len(info) == 0:
        raise ImportError('Attempting to import zero expression data, please remove expression data from study.')
    elif len(info) == 1:
        result = info[0]
    else:
        result = info[0]
        for i in range(1, len(info)):
            result = pd.merge(result, info[i], on='Hugo_Symbol')
    result.replace(np.nan, 0, inplace=True)

    helper.working_on(verb, message='Writing all FPKM data ...')
    result.to_csv(output_file, sep='\t', index=None)


def generate_expression_zscore(exports_config: Config.Config, study_config: Config.Config, verb):
    input_file = os.path.join(study_config.config_map['output_folder'],
                              'data_{}.txt'.format(config2name_map[exports_config.type_config]))

    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.type_config + '_ZSCORES']))

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