__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "1.0"

import os
import subprocess
import argparse


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="Importer script for cBioPortal.")

    parser.add_argument("-f", "--folder",
                        help="The location of the study folder.",
                        metavar='FOLDER',
                        required=True)
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL',
                        required=True)
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
    subprocess.call(command, shell=True)

def get_shell(command: str, verb) -> str:
    working_on(verb, message=command)
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    return output.decode('utf-8')


def export_study_to_cbioportal(key: str, study_folder: str, cbioportal_url, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    log_file = os.path.join(os.path.abspath(study_folder), 'import_log.txt')
    # Copying folder to cBioPortal
    working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    call_shell("ssh {} debian@{} ' rm -r ~/oicr_studies/{}; mkdir ~/oicr_studies/{}'".format(key,
                                                                                             cbioportal_url,
                                                                                             base_folder,
                                                                                             base_folder), verb)

    # Copy over
    call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_url),
               verb)

    working_on(verb)

    # Import study to cBioPortal
    working_on(verb, message='Importing study to cBioPortal...')

    result = get_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                       "sudo ./metaImport.py -s ~/oicr_studies/{} "
                       "-u http://{} -o'; "
                       "echo 'CBIOPORTAL_EXIT_CODE:' $?".format(key, cbioportal_url,
                                        base_folder,
                                        cbioportal_url), verb)
    print(result)
    valid = int(list(filter(None, [a if a.startswith('CBIOPORTAL_EXIT_CODE: ') else '' for a in result.split('\n')]))[0].strip('CBIOPORTAL_EXIT_CODE: '))
    print(valid)

    f = open(os.path.abspath(os.path.join(study_folder, 'import_log.txt')), 'w')
    f.write(result)
    f.flush()
    f.close()

    print('cBioPortal exit code: {}'.format(valid))
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
    export_study_to_cbioportal(args.key, args.folder, args.url, True)


if __name__ == '__main__':
    main()
