import argparse
import os

import pandas as pd

from lib.constants import constants
from lib.support import Config, helper

args2config_map = constants.args2config_map


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(
        description="janus "
                    "(https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate an importable study for "
                    "a cBioPortal instance. Recommended usage can be seen in the examples located in ../study_input/ .")
    config = parser.add_argument_group('Study Arguments (Required):')

    config.add_argument("-c", "--config",
                        help="The location of the study config file, in essence a set of command-line arguments. "
                             "Recommended usage is with configuration file. File data can be overridden by command-line"
                             " arguments.",
                        metavar='FILE')
    config.add_argument("-o", "--output-folder",
                        type=lambda folder: os.path.abspath(folder),
                        help="The main folder of the study you want to generate.",
                        metavar='FOLDER',
                        required=True)
    config.add_argument("-t", "--type-of-cancer",
                        help="The type of cancer.",
                        metavar='TYPE')
    config.add_argument("-i", "--cancer-study-identifier",
                        help="The cancer study ID.",
                        metavar='ID')
    config.add_argument("-N", "--name",
                        help="The name of the study.",
                        metavar='NAME')
    config.add_argument("-n", "--short-name",
                        help="A short name for the study.",
                        metavar='NAME')
    config.add_argument("-d", "--description",
                        help="A description of the study.",
                        metavar='DESCRIPTION')
    config.add_argument("--path",
                        help="Path of Janus.py",
                        metavar='PATH',
                        required=True)
    # TODO:: Add Option to generate a specific case list

    config_spec = parser.add_argument_group('Overridable Required Configuration File Specifiers:')

    config_spec.add_argument('--' + 'sample-info',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. REQUIRED.'.format('sample-info',
                                                                         args2config_map['sample_info']))
    config_spec.add_argument('--' + 'patient-info',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. REQUIRED.'.format('patient-info',
                                                                         args2config_map['patient_info']))
    config_spec.add_argument('--' + 'cancer-type',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. REQUIRED*'.format('cancer-type',
                                                                         args2config_map['cancer_type']))


    config_data = parser.add_argument_group('Overridable Optional Data-type Configuration File Specifiers:')

    config_data.add_argument('--' + 'mutation-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. OPTIONAL'.format('mutation-data',
                                                                        args2config_map['mutation_data']))
    config_data.add_argument('--' + 'segmented-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. The segmented data file will normally generate _CNA and _log2CNA'
                                  ' files. See documentation if you do not want this. '
                                  '                    OPTIONAL'.format('segmented-data',
                                                                        args2config_map['segmented_data']))
    config_data.add_argument('--' + 'continuous-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file.See the docs.'
                                  '                    OPTIONAL'.format('continuous-data',
                                                                        args2config_map['continuous_data']))
    config_data.add_argument('--' + 'discrete-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. See the docs.'
                                  '                    OPTIONAL'.format('discrete-data',
                                                                        args2config_map['discrete_data']))
    config_data.add_argument('--' + 'expression-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file.'
                                  ' files. See the documentation if you do not want this.'
                                  '                    OPTIONAL'.format('expression-data',
                                                                        args2config_map['expression_data']))
    #TODO:: Remove this from here, add it as an option within expression_data
    config_data.add_argument('--' + 'expression-zscores-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file.'
                                  ' files. See the documentation if you do not want this.'
                                  '                    OPTIONAL'.format('expression-zscores-data',
                                                                        args2config_map['expression_zscores_data']))
    config_data.add_argument('--' + 'fusion-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('fusion-data',
                                                                        args2config_map['fusion_data']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'methylation-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('methylation-data',
                                                                        args2config_map['methylation_data']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'protein-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('protein-data',
                                                                        args2config_map['protein_data']),
                             metavar='UNSUPPORTED')
    config_spec.add_argument('--' + 'timeline-info',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('timeline-info',
                                                                        args2config_map['timeline_info']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'gistic2-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('gistic2-data',
                                                                        args2config_map['gistic2_data']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'mutsig-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('mutsig-data',
                                                                        args2config_map['mutsig_data']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'gene-panel-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('gene-panel-data',
                                                                        args2config_map['gene_panel_data']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'gene-set-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('gene-set-data',
                                                                        args2config_map['gene_set_data']),
                             metavar='UNSUPPORTED')
    config_data.add_argument('--' + 'custom-case-list',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. UNSUPPORTED. See the docs.       '
                                  'OPTIONAL --         UNSUPPORTED'.format('custom-case-list',
                                                                           args2config_map['custom_case_list']),
                             metavar='UNSUPPORTED')
    parser.add_argument("-k", "--key",
                        type=lambda key: os.path.abspath(key),
                        help="The RSA key to cBioPortal. Should have appropriate read write restrictions",
                        metavar='FILE',
                        default='')
    parser.add_argument("-p", "--push",
                        action="store_true",
                        help="Push the generated study to the cBioPortal Instance")
    parser.add_argument("-u", "--url",
                        help="Override the url for cBioPortal instance DO NOT include https",
                        metavar='URL',
                        default=constants.cbioportal_url)
    # TODO:: Consider having multiple levels of verbosity
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    return parser


def add_cli_args(study_config: Config.Config, args: argparse.Namespace, verb) -> Config.Config:
    meta_args = ['type_of_cancer', 'cancer_study_identifier', 'name', 'short_name', 'description', 'output_folder']

    helper.working_on(verb, 'Merging Config information from command line and configuration file')

    dictionary = {k: v for k, v in vars(args).items() if v is not None}
    for each in dictionary.keys():
        if each in meta_args:
            study_config.config_map[each] = dictionary[each]

        elif any([each.endswith('_data'), each.endswith('_info')]):
            study_config.data_frame.append(pd.DataFrame({'TYPE': args2config_map[each], 'FILE': dictionary[each]}))

    study_config.type_config = 'study'

    # Check to ensure minimum conditions are filled.
    if not set(meta_args).issubset(set(study_config.config_map.keys())):
        raise IOError('The minimum number of arguments have not been provided in the file and/or command-line arguments'
                      '\nSee: {}'.format(meta_args))
    return study_config