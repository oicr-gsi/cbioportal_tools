#! /usr/bin/env python3

"""Script to remove data from cBioPortal"""

import argparse
import logging

from support.helper import call_shell, configure_logger, restart_tomcat

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


def delete_study(key: str, study_config: str, cbioportal_url, logger):
    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with logger
    if not key == '':
        key = '-i ' + key
    base_folder = 'study_removal'
    # Copying folder to cBioPortal
    logger.info('Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    call_shell("ssh {} debian@{} 'rm ~/oicr_studies/{}'".format(key,
                                                                cbioportal_url,
                                                                base_folder,
                                                                base_folder), verb)

    # Copy over
    call_shell('scp {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_config, cbioportal_url), verb)

    # Import study to cBioPortal
    logger.info('Importing study to cBioPortal...')

    # TODO do this without calling out to the shell
    ec = call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                       "./cbioportalImporter.py --command remove-study --meta_filename ~/oicr_studies/meta_study.txt; "
                       "rm ~/oicr_studies/meta_study.txt' ".format(key,
                                                                   cbioportal_url,
                                                                   base_folder,
                                                                   cbioportal_url), verb)
    # check the shell exit code
    if ec == 1:
        logger.error('Validation of study failed. There could be something wrong with the data, please analyse cBioPortalImporter.py output. Exiting.')
        exit(1)
    elif exit_code == 3:
        logger.warn('Validation of study succeeded with warnings. Don\'t worry about it, unless you think it\'s important.')
    elif exit_code == 0:
        logger.info('Validation of study succeeded without warnings')
    else:
        logger.critical('Unexpected error code %i from cbioportal importer; exiting.' % ec)
        exit(1)

def main(args):
    study = 'meta_study.txt'
    logger = configure_logger(logging.getLogger(__name__), args.log_path, args.debug, args.verbose)
    config = open(study, 'w+')
    config.write('cancer_study_identifier:{}\ntype_of_cancer:\nshort_name:\nname:\ndescription:\r'.format(args.id))
    config.flush()
    config.close()
    delete_study(args.key, study, args.url, logger)
    restart_tomcat(args.url, args.key, True)
