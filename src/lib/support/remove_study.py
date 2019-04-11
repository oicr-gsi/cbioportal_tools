#TODO:: Remove a study given an Identifier...
__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "1.0"

import os
import subprocess
import argparse


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="Importer script for cBioPortal.")

    parser.add_argument("-i", "--id",
                        help="The cancer study ID.",
                        metavar='ID')
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL')
    parser.add_argument("-k", "--key",
                        help="The location of the cBioPortal Key.",
                        metavar='KEY',
                        default='')
    return parser

def working_on(verbosity, message='Success!\n'):
    # Method is for verbose option. Prints Success if no parameter specified
    if verbosity:
        print(message)


def stars():
    # Prints a row of stars
    for a in range(100):
        print('*', end="")
    print('')


def call_shell(command: str, verb):
    working_on(verb, message=command)
    output = subprocess.call(command, shell=True)
    return output


def export_study_to_cbioportal(key: str, study_config: str, cbioportal_url, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = 'study_removal'
    log_file = os.path.join(os.path.abspath(study_config), 'import_log.txt')
    # Copying folder to cBioPortal
    working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    call_shell("ssh {} debian@{} ' rm -r ~/oicr_studies/{}; mkdir ~/oicr_studies/{}'".format(key,
                                                                                             cbioportal_url,
                                                                                             base_folder,
                                                                                             base_folder), verb)

    # Copy over
    call_shell('scp {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_config, cbioportal_url),
               verb)

    working_on(verb)

    # Import study to cBioPortal
    working_on(verb, message='Importing study to cBioPortal...')

    valid = call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                       "sudo ./metaImport.py -s ~/oicr_studies/{} "
                       "-u http://{} -o' | "
                       "tee {}".format(key, cbioportal_url,
                                       base_folder,
                                       cbioportal_url,
                                       log_file), verb)

    if   valid == 1:
        stars()
        stars()
        print('Validation of study failed. There could be something wrong with the data, please analyse cBioPortal\'s '
              'message above. ')
        stars()
        stars()
        exit(1)
    elif valid == 3:
        stars()
        print('Validation of study succeeded with warnings. Don\'t worry about it, unless you think it\'s important.')
        stars()
    elif valid == 0:
        stars()
        print('This validated with 0 warnings, Congrats!!!')
        stars()
    else:
        stars()
        print('I think something broke really bad, raise an issue about what happened...')
        stars()
        stars()
        exit(1)

    call_shell("ssh {} debian@{} 'sudo systemctl stop  tomcat'".format(key, cbioportal_url), verb)
    call_shell("ssh {} debian@{} 'sudo systemctl start tomcat'".format(key, cbioportal_url), verb)

    working_on(verb)

def main():
    args = define_parser().parse_args()
    config = open(args.id+'.txt', 'w+')
    config.write('')
    export_study_to_cbioportal(args.key, config, args.url, True)


if __name__ == '__main__':
    main()
