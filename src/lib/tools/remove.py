__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import argparse

from ..support.helper import stars, working_on, call_shell, restart_tomcat


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="Importer script for cBioPortal.")

    parser.add_argument("-i", "--id",
                        help="The cancer study ID.",
                        metavar='ID',
                        required=True)
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL',
                        required=True)
    parser.add_argument("-k", "--key",
                        help="The location of the cBioPortal Key.",
                        metavar='KEY')
    return parser


def delete_study(key: str, study_config: str, cbioportal_url, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = 'study_removal'
    # Copying folder to cBioPortal
    working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    call_shell("ssh {} debian@{} 'rm ~/oicr_studies/{}'".format(key,
                                                                cbioportal_url,
                                                                base_folder,
                                                                base_folder), verb)

    # Copy over
    call_shell('scp {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_config, cbioportal_url), verb)

    working_on(verb)

    # Import study to cBioPortal
    working_on(verb, message='Importing study to cBioPortal...')

    valid = call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                       "./cbioportalImporter.py --command remove-study --meta_filename ~/oicr_studies/meta_study.txt; "
                       "rm ~/oicr_studies/meta_study.txt' ".format(key,
                                                                   cbioportal_url,
                                                                   base_folder,
                                                                   cbioportal_url), verb)

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
    working_on(verb)


def main(args):
    study = 'meta_study.txt'
    config = open(study, 'w+')
    config.write('cancer_study_identifier:{}\ntype_of_cancer:\nshort_name:\nname:\ndescription:\r'.format(args.id))
    config.flush()
    config.close()
    delete_study(args.key, study, args.url, True)
    restart_tomcat(args.url, args.key, True)
