import os

import numpy as np
import pandas as pd

from Janus import Information
from lib.constants import cbiowrap_export
from lib.support import Config, helper


def generate_cbiowrap_configs(information: Information, study_config: Config.Config, verb):
    # Copy fixed config.
    ini = open('lib/support/cbiowrap_config_template.ini', 'r')
    fixed = ini.readlines()
    ini.close()

    # Write wanted_columns.txt
    helper.working_on(verb, 'Writing wanted at {}'.format(helper.get_cbiowrap_file(study_config, 'wanted_columns.txt')))
    if 'MAF' not in [each.type_config for each in information]:
        wanted = helper.get_cbiowrap_file(study_config, 'wanted_columns.txt')
        helper.clean_folder(os.path.dirname(wanted))
        o = open(wanted, 'w+')
        o.write('')
        o.flush()
        o.close()

    info = information.copy()
    for each in info:
        if each.type_config in cbiowrap_export:
            for i in range(each.data_frame.shape[0]):
                each.data_frame['FILE_NAME'][i] = os.path.join(each.config_map['input_folder'],
                                                               each.data_frame['FILE_NAME'][i])

    # Generate Mapping.csv
    [i.data_frame.rename(columns={'FILE_NAME': i.type_config}, inplace=True) for i in info]
    # Merge all data_frames, and gather mutation, seg and gep
    # TODO:: Convert the TUMOR_ID to a SAMPLE_ID
    if len(info) == 0:
        result = Config.Config({}, pd.DataFrame('PATIENT_ID', 'TUMOR_ID'), '')
    elif len(info) == 1:
        result = info[0]
    else:
        result = info[0]
        for i in range(1, len(info)):
            result.data_frame = pd.merge(result.data_frame, info[i].data_frame, on=['PATIENT_ID', 'TUMOR_ID'])

    result.data_frame.replace(np.nan, 'NA', inplace=True)

    for col in cbiowrap_export:
        if col not in result.data_frame:
            result.data_frame[col] = 'NA'


    csv = result.data_frame[['PATIENT_ID', 'TUMOR_ID', *cbiowrap_export]]

    helper.working_on(verb, 'Writing mapping.csv at {}'.format(helper.get_cbiowrap_file(study_config, 'mapping.csv')))
    csv.to_csv(helper.get_cbiowrap_file(study_config, 'mapping.csv'), header=False, index=False)
    # Write arguments to config.ini
    helper.working_on(verb, 'Writing Config.ini at {}'.format(helper.get_cbiowrap_file(study_config, 'config.ini')))
    out = open(helper.get_cbiowrap_file(study_config, 'config.ini'), 'w+')
    out.writelines(fixed)
    out.write('\nstudy="{}"'.format(study_config.config_map['cancer_study_identifier']))
    out.write('\ntypec="{}"'.format(study_config.config_map['type_of_cancer']))
    out.write('\noutdir="{}"'.format(study_config.config_map['output_folder']))
    out.write('\nvepkeep="{}"'.format(helper.get_cbiowrap_file(study_config, 'wanted_columns.txt')))
    out.write('\nmapfile="{}"'.format(helper.get_cbiowrap_file(study_config, 'mapping.csv')))


def run_cbiowrap(study_config: Config.Config, verb):
    helper.call_shell('cd /.mounts/labs/gsiprojects/gsi/cBioGSI/kchandan/cBioWrap/; '
                      './cBioWrap.sh -c {}'.format(helper.get_cbiowrap_file(study_config, 'config.ini')), verb)

    os.rename(os.path.join(study_config.config_map['output_folder'], 'cbioportal_import_data'),
              os.path.join(study_config.config_map['output_folder'], study_config.config_map['cancer_study_identifier']))

    study_config.config_map['output_folder'] = os.path.join(study_config.config_map['output_folder'],
                                                            study_config.config_map['cancer_study_identifier'])