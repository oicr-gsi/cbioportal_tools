import os
import subprocess
import argparse


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="Importer script for cBioPortal.")

    parser.add_argument("-f", "--folder",
                        help="The location of the study folder.",
                        metavar='FOLDER')
    parser.add_argument("-i", "--ip",
                        help="The location of the cBioPortal instance.",
                        metavar='IP')
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='IP')
    parser.add_argument("-k", "--key",
                        help="The location of the cBioPortal Key.",
                        metavar='KEY')
    return parser

def working_on(verbosity, message='Success!\n'):
    # Method is for verbose option. Prints Success if no parameter specified
    if verbosity:
        print(message)


def call_shell(command: str, verb):
    working_on(verb, message=command)
    output = subprocess.call(command, shell=True)
    return output


def export_study_to_cbioportal(key: str, study_folder: str, cbioportal_ip, cbioportal_url, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
               "rm -r ~/oicr_studies/{}; "
               "mkdir ~/oicr_studies/{}'".format(key, cbioportal_ip, base_folder, base_folder), verb)

    # Copy over
    call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_ip),
               verb)

    working_on(verb)

    # Import study to cBioPortal
    working_on(verb, message='Importing study to cBioPortal...')

    call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
               "sudo ./metaImport.py -s ~/oicr_studies/{} "
               "-u http://{} -o'".format(key, cbioportal_ip,
                                         base_folder,
                                         cbioportal_url), verb)

    call_shell("ssh {} debian@{} 'sudo systemctl stop  tomcat'".format(key, cbioportal_ip), verb)
    call_shell("ssh {} debian@{} 'sudo systemctl start tomcat'".format(key, cbioportal_ip), verb)

    working_on(verb)

def main():
    args = define_parser().parse_args()
    export_study_to_cbioportal(args.key, args.folder, args.ip, args.url, True)


if __name__ == '__main__':
    main()
