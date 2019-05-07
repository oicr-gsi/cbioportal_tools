__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"


### this script is for generation of an import folder

import pandas as pd
import argparse
import typing
import os

from lib.constants import constants
from lib.study_generation import data, meta, case
from lib.support import Config, helper, cbioportal_interface


## a map of command line arguments to internal terms
args2config_map = constants.args2config_map

Information = typing.List[Config.Config]


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    generator = argparse.ArgumentParser(
        description="janus "
                    "(https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate an importable study for "
                    "a cBioPortal instance. Recommended usage can be seen in the examples located in ../study_input/ .")
    generator.register('action', 'pipes', DocstringAction)
    config = generator.add_argument_group('Study Arguments (Required):')

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

    config_spec = generator.add_argument_group('Overridable Required Configuration File Specifiers:')

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

    config_data = generator.add_argument_group('Overridable Optional Data-type Configuration File Specifiers:')

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

    pipeline = generator.add_argument_group('Pipelines', 'Pipelines printing')
    pipeline.add_argument("-P", "--pipelines",
                          choices=constants.supported_pipe.keys(),
                          metavar='TYPE',
                          nargs='?',
                          action='pipes',
                          help="Query which pipelines are supported and exit. "
                               "Types are: {}".format(constants.supported_pipe.keys()))

    options = generator.add_argument_group('Other Supporting Optional Arguments:')
    options.add_argument("-k", "--key",
                         type=lambda key: os.path.abspath(key),
                         #if not key == '' else helper.exit_program('Appropriate key for cBioPortal instance was not provided', 1),
                         help="The RSA key to cBioPortal. Should have appropriate read write restrictions",
                         metavar='FILE',
                         default='')
    options.add_argument("-p", "--push",
                         action="store_true",
                         help="Push the generated study to the cBioPortal Instance")
    options.add_argument("-u", "--url",
                         help="Override the url for cBioPortal instance DO NOT include https",
                         metavar='URL',
                         default=constants.cbioportal_url)

    # TODO:: Consider having multiple levels of verbosity
    options.add_argument("-v", "--verbose",
                         action="store_true",
                         default=False,
                         help="Makes program verbose")
    return generator


def resolve_priority_queue(information: Information) -> Information:
    score = {}
    # Initialize scores
    for each in information:
        score[each.type_config] = 0

    # Calculate Scores based on directed graph traversal
    for each in information:
        if 'pipeline' in each.config_map.keys():
            type_config = each.config_map['pipeline']
        else:
            continue
        while True:
            if not (type_config in constants.meta_info_map.keys()):
                break
            else:
                score[type_config] += 1
            type_config = [x.config_map['pipeline'] for x in information if x.type_config == type_config]
            if len(type_config) > 1:
                # This really only works if there is one config of each type
                # Right now this is not a problem, could this be one day?
                raise ImportError('ERROR:: 2 or more info objects of the same type???')
            else:
                type_config = type_config[0]

    # Sort list based on new scores.
    information.sort(key=lambda config: score [config.type_config], reverse=True)
    return information


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


class DocstringAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        output_set = constants.supported_pipe[values]
        output_set.append('FILE')
        print('The supported formats are {}'.format(output_set))
        parser.exit()


def main(args):
    verb = args.verbose
    path = args.path
    constants.cbioportal_url = args.url

    # TODO:: Fail gracefully if something breaks
    ### study_config defines the study, arguments and files to use for the data
    if args.config:
        ### load from file
        study_config = Config.get_single_config(args.config, 'study', 'study',verb)
    else:
        ### create an empty dataframe
        study_config = Config.Config({}, pd.DataFrame(columns=['TYPE', 'FILE_NAME']), 'study','study')

    ### command line argument can be provided that will overide what is in the configuation files
    add_cli_args(study_config, args, verb)


    [information, clinic_data, custom_list] = Config.gather_config_set(study_config, args, verb)
    print("leaving early")
    exit()
    information = resolve_priority_queue(information)

    [print('Informational Files {}:\n{}\n'.format(a.type_config, a)) for a in information] if verb else print(),
    [print('Clinical List Files {}:\n{}\n'.format(a.type_config, a)) for a in clinic_data] if verb else print(),
    [print('Customized Case Set {}:\n{}\n'.format(a.type_config, a)) for a in custom_list] if verb else print(),

    # Clean Output Folder/Initialize it
    helper.clean_folder(study_config.config_map['output_folder'])

    for each in information:
        print(each)

        meta.generate_meta_type(each.type_config, each.config_map, study_config, verb)
        data.generate_data_type(each, study_config, path, verb)
        case.generate_case_list(each, study_config, verb)

    for each in clinic_data:
        meta.generate_meta_type(each.type_config, each.config_map, study_config, verb)
        data.generate_data_clinical(each, study_config, verb)

    for each in custom_list:
        case.generate_case_list(each, study_config, verb)

    meta.generate_meta_study(study_config, verb)

    # export to cbioportal!
    if args.key or args.push:
        cbioportal_interface.validate_study(args.key, study_config.config_map['output_folder'], verb)
        cbioportal_interface.export_study_to_cbioportal(args.key, study_config.config_map['output_folder'], verb)
        helper.restart_tomcat(constants.cbioportal_url, args.key, verb)
        # TODO:: Make the validation step ensure that it doesn't overwrite an existing study

    helper.stars()
    helper.stars()
    helper.working_on(True, message='CONGRATULATIONS! Your study should now be imported!')
    helper.stars()
    helper.working_on(True, message='Output folder: {}'.format(study_config.config_map['output_folder']))
    helper.working_on(True, message='Study Name: {}'.format(study_config.config_map['name']))
    helper.working_on(True, message='Study ID: {}'.format(study_config.config_map['cancer_study_identifier']))
    helper.stars()
    helper.stars()
