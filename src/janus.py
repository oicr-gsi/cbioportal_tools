__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import argparse
import os
import typing

import pandas as pd

# Other Scripts
from lib.support import Config, helper
from lib.constants.constants import args2config_map, cbioportal_ip, cbioportal_url
from lib.study_generation import data, meta, case

Information = typing.List[Config.Config]

def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(
        description="janus "
                    "(https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate an importable study for "
                    "a cBioPortal instance. Recommended usage can be seen in the examples located in ../study_input/ .")
    parser.add_argument("-c", "--config",
                        help="The location of the study config file, in essence a set of command-line arguments. "
                             "Recommended usage is with configuration file. File data can be overridden by command-line"
                             " arguments.",
                        metavar='FILE')
    parser.add_argument("-o", "--output-folder",
                        type=lambda folder: os.path.abspath(folder),
                        help="The main folder of the study you want to generate.",
                        metavar='FOLDER',
                        required=True)
    parser.add_argument("-t", "--type-of-cancer",
                        help="The type of cancer.",
                        metavar='TYPE')
    parser.add_argument("-i", "--cancer-study-identifier",
                        help="The cancer study ID.",
                        metavar='ID')
    parser.add_argument("-N", "--name",
                        help="The name of the study.",
                        metavar='NAME')
    parser.add_argument("-n", "--short-name",
                        help="A short name for the study.",
                        metavar='NAME')
    parser.add_argument("-d", "--description",
                        help="A description of the study.",
                        metavar='DESCRIPTION')
    # TODO:: Add Option to generate a specific case list

    config_spec = parser.add_argument_group('Overridable Required Configuration File Specifiers')

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
    config_spec.add_argument('--' + 'timeline-info',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('timeline-info',
                                                                        args2config_map['timeline_info']))


    config_data = parser.add_argument_group('Overridable Optional Data-type Configuration File Specifiers')

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
    config_data.add_argument('--' + 'expression-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. The expression data file will normally generate _zscores'
                                  ' files. See the documentation if you do not want this.'
                                  '                    OPTIONAL'.format('expression-data',
                                                                        args2config_map['expression_data']))
    config_data.add_argument('--' + 'CNA-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('CNA-data',
                                                                        args2config_map['CNA_data']))
    config_data.add_argument('--' + 'log2CNA-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('log2CNA-data',
                                                                        args2config_map['log2CNA_data']))
    config_data.add_argument('--' + 'fusions-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('fusions-data',
                                                                        args2config_map['fusions_data']))
    config_data.add_argument('--' + 'methylation-hm27-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('methylation-hm27-data',
                                                                        args2config_map['methylation_hm27_data']))
    config_data.add_argument('--' + 'rppa-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('rppa-data',
                                                                        args2config_map['rppa_data']))
    config_data.add_argument('--' + 'gistic-genes-amp-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('gistic-genes-amp-data',
                                                                        args2config_map['gistic_genes_amp_data']))
    config_data.add_argument('--' + 'mutsig-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('mutsig-data',
                                                                        args2config_map['mutsig_data']))
    config_data.add_argument('--' + 'GENE-PANEL-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('GENE-PANEL-data',
                                                                        args2config_map['GENE_PANEL_data']))
    config_data.add_argument('--' + 'gsva-scores-data',
                             help='Location of {} configuration file: will override {} specification '
                                  'in the config file. THIS HAS NOT BEEN IMPLEMENTED YET'
                                  'See the docs        OPTIONAL'.format('gsva-scores-data',
                                                                        args2config_map['gsva_scores_data']))


    parser.add_argument("-k", "--key",
                        type=lambda key: os.path.abspath(key),
                        help="The RSA key to cBioPortal. Should have appropriate read write restrictions",
                        metavar='FILE',
                        default='/u/kchandan/cbioportal.pem')
    parser.add_argument("-p", "--push",
                        action="store_true",
                        help="Push the generated study to the cBioPortal Instance")
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


def export_study_to_cbioportal(key: str, study_folder: str, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    helper.call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                      "rm -r ~/oicr_studies/{}; "
                      "mkdir ~/oicr_studies/{}'".format(key, cbioportal_ip, base_folder, base_folder), verb)

    # Copy over
    helper.call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_ip),
                      verb)

    helper.working_on(verb)

    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')

    helper.call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                      "sudo ./metaImport.py -s ~/oicr_studies/{} "
                      "-u http://{} -o'".format(key, cbioportal_ip,
                                                base_folder,
                                                cbioportal_url), verb)

    helper.call_shell("ssh {} debian@{} 'sudo systemctl stop  tomcat'".format(key, cbioportal_ip), verb)
    helper.call_shell("ssh {} debian@{} 'sudo systemctl start tomcat'".format(key, cbioportal_ip), verb)

    helper.working_on(verb)


def validate_study(key, study_folder, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Validating study ...')

    helper.call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                      "rm -r ~/oicr_studies/{}; "
                      "mkdir ~/oicr_studies/{}'".format(key, cbioportal_ip, base_folder, base_folder), verb)

    # Copy over
    helper.call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_ip),
                      verb)

    helper.working_on(verb)


    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')

    valid = helper.call_shell("ssh {} debian@{} "
                              "'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                              "sudo ./validateData.py -s ~/oicr_studies/{} "
                              "-u http://{} "
                              "-v -m'".format(key, cbioportal_ip,
                                              base_folder,
                                              cbioportal_url), verb)

    if   valid == 1:
        helper.stars()
        helper.stars()
        print('Validation of study failed. There could be something wrong with the data, please analyse cBioPortal\'s '
              'message above. ')
        exit(1)
        helper.stars()
        helper.stars()
    elif valid == 3:
        helper.stars()
        print('Validation of study succeeded with warnings. Don\'t worry about it, unless you think it\'s important.')
        helper.stars()
    else:
        helper.stars()
        print('Either this validated with 0 warnings or something broke really bad, raise an issue if it\'s the latter')
        helper.stars()
    helper.working_on(verb)



def main():
    # TODO:: Ensure absolute paths for helper program files: ie seg2gene.R
    args = define_parser().parse_args()
    verb = args.verbose
    # TODO:: Fail gracefully if something breaks

    if args.config:
        study_config = Config.get_single_config(args.config, 'study', verb)
    else:
        study_config = Config.Config({}, pd.DataFrame(columns=['TYPE', 'FILE_NAME']), 'study')
    add_cli_args(study_config, args, verb)

    [information, clinic_data] = Config.gather_config_set(study_config, args, verb)

    [print('Informational Files {}:\n{}\n'.format(a.type_config, a)) for a in information] if verb else print(),
    [print('Clinical List Files {}:\n{}\n'.format(a.type_config, a)) for a in clinic_data] if verb else print(),

    # Clean Output Folder/Initialize it
    helper.clean_folder(study_config.config_map['output_folder'])

    for each in information:
        meta.generate_meta_type(each.type_config, each.config_map, study_config, verb)
        data.generate_data_type(each, study_config, verb)
        case.generate_case_list(each, study_config)

    for each in clinic_data:
        meta.generate_meta_type(each.type_config, each.config_map, study_config, verb)
        data.generate_data_clinical(each, study_config, verb)
    meta.generate_meta_study(study_config, verb)

    # export to cbioportal!
    if args.key or args.push:
        validate_study(args.key, study_config.config_map['output_folder'], verb)
        export_study_to_cbioportal(args.key, study_config.config_map['output_folder'], verb)
        # TODO:: Make the validation step ensure that it doesn't overwrite an existing study

    helper.stars()
    helper.working_on(verb, message='CONGRATULATIONS! Your study should now be imported!')
    helper.stars()
    helper.working_on(verb, message='Output folder: {}'.format(study_config.config_map['output_folder']))
    helper.working_on(verb, message='Study Name: {}'.format(study_config.config_map['name']))
    helper.stars()


if __name__ == '__main__':
    main()
