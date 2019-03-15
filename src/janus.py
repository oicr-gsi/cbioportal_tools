__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import argparse
import os
import typing

import pandas as pd

# Other Scripts
from lib.support import Config, cbiowrap_interface, helper
from lib.constants import args2config_map
from lib.study_generation import data, meta

Information = typing.List[Config.Config]

def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(
        description="janus "
                    "(https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate an importable study for "
                    "a cBioPortal instance. Recommended usage can be seen in the examples located in ../study_input/ .")
    parser.add_argument("-c", "--config",
                        help="The location of the study config file, containing command line arguments as key/value pairs",
                        metavar='FILE')
    parser.add_argument("-o", "--output-folder",
                        type=lambda folder: os.path.abspath(folder),
                        help="The main folder of the study you want to generate.",
                        metavar='FOLDER',
                        default='new_study/')
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

    parser.add_argument("-m", "--memory",
                        type=lambda x: int(int(x) * (1000**3)),
                        help="The amount of virtual memory given to the instance in Gb",
                        metavar='V_MEM',
                        default=-1)

    parser.add_argument("-k", "--key",
                        type=lambda key: os.path.abspath(key),
                        help="The RSA key to cBioPortal. Should have appropriate read write restrictions",
                        metavar='FILE',
                        default='/u/kchandan/cbioportal.pem')
    parser.add_argument("-p", "--push",
                        action="store_true",
                        help="Push the generated study to the cBioPortal Instance")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Forces overwriting of data_cancer_type.txt file and *.maf files.")
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
        raise IOError('The minimum number of arguments have not been provided. \nSee: {}'.format(meta_args))
    return study_config


def export_study_to_cbioportal(key, study_folder, verb):
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Copying folder to cBioPortal instance at 10.30.133.80 ...')

    helper.call_shell("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                      "rm -r ~/oicr_studies/{}; "
                      "mkdir ~/oicr_studies/{}'".format(key, base_folder, base_folder), verb)

    # Copy over
    helper.call_shell('scp -r -i {} {} debian@10.30.133.80:/home/debian/oicr_studies/'.format(key, study_folder), verb)

    helper.working_on(verb)

    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')

    helper.call_shell("ssh -i {} debian@10.30.133.80 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                      "sudo ./metaImport.py -s ~/oicr_studies/{} "
                      "-u http://10.30.133.80:8080/cbioportal -o'".format(key, base_folder), verb)

    helper.call_shell("ssh -i {} debian@10.30.133.80 'sudo systemctl stop  tomcat'".format(key), verb)
    helper.call_shell("ssh -i {} debian@10.30.133.80 'sudo systemctl start tomcat'".format(key), verb)

    helper.working_on(verb)


def main():
    args = define_parser().parse_args()
    verb = args.verbose
    force = args.force
    memory = args.memory

    # TODO:: Fail gracefully if some arguments are not given

    if args.config:
        study_config = Config.get_single_config(args.config, 'study', verb)
    else:
        study_config = Config.Config({}, pd.DataFrame(columns=['TYPE', 'FILE']), 'study')
    add_cli_args(study_config, args, verb)

    [information, clinic_data, cancer_type] = Config.gather_config_set(study_config, args, verb)

    [print('Information File {}:\n{}\n'.format(a.type_config, a)) for a in information] if verb else print(),
    [print('\nClinical Files {}:\n{}\n'.format(a.type_config, a)) for a in clinic_data] if verb else print(),

    # Clean Output Folder/Initialize it
    helper.clean_folder(study_config.config_map['output_folder'])

    for each in information:
        data.generate_data_type(each, study_config, force, verb)

    # Generate Config.ini file, Mapping.csv and wanted_columns.txt
    cbiowrap_interface.generate_cbiowrap_configs(information, study_config, verb)

    # run cBioWrap.sh
    cbiowrap_interface.run_cbiowrap(study_config, verb)

    # Overwrite some of the meta files (Optional)
    # Generate CANCER_TYPE
    if type(cancer_type) == Config.Config:
        meta.generate_meta_type(cancer_type, study_config, verb)
        data.generate_data_type(cancer_type, study_config, force, verb)
    for each in information:
        meta.generate_meta_type(each, study_config, verb)
    for each in clinic_data:
        meta.generate_meta_type(each, study_config, verb)
        data.generate_data_clinical(each, study_config, verb)
    meta.generate_meta_study(study_config, verb)

    # export to cbioportal!
    if args.key:
        export_study_to_cbioportal(args.key, study_config.config_map['output_folder'], verb)

    helper.stars()
    helper.working_on(verb, message='CONGRATULATIONS! A minimal study is now be complete!')
    helper.working_on(verb, message='Output folder: {}'.format(study_config.config_map['output_folder']))
    helper.stars()


if __name__ == '__main__':
    main()
