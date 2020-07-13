#! /usr/bin/env python3

"""Script to query cBioPortal"""

import argparse
import logging
import sys

from lib.support.helper import configure_logger, get_shell


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal SQL Query Script.")

    # INTERACTION
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL',
                        required=True)
    parser.add_argument("-p", "--properties",
                        help="portal.properties file path. Default ~/cbioportal/portal.properties",
                        metavar='PATH',
                        default='~/cbioportal/portal.properties')
    parser.add_argument("-k", "--key",
                        help="The location of the cBioPortal Key.",
                        metavar='KEY',
                        default='')

    # QUERY
    parser.add_argument("-t", "--type-of-cancer",
                        help="Query the types of cancer in the cBioPortal Database",
                        action='store_true')
    parser.add_argument("-g", "--gene-panel",
                        help="Query the gene-panels in the cBioPortal Database",
                        action='store_true')
    parser.add_argument("-b", "--border",
                        help="Disables borders around the query.",
                        action='store_true',
                        default=False)

    return parser


def retrieve_auth(key, url, properties_path, logger) -> [str, str]:
    if not key == '':
        key = '-i ' + key

    out = get_shell("ssh {} debian@{} '"
                    "grep -E 'db.user|db.password' {}'".format(key,
                                                               url,
                                                               properties_path), True)
    logger.info(out)
    [user, password] = out.strip().splitlines(keepends=False)
    user = user.replace('db.user=', '')
    password = password.replace('db.password=', '')

    return [user, password]


def query_portal(key: str, cbioportal_url: str, user: str, password: str, query_toc: bool, query_gp: bool, border, logger):
    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with calls to a logger

    if not key == '':
        key = '-i ' + key

    if border:
        border = '-B'
    else:
        border = ''

    if query_toc:
        out = get_shell("ssh {} debian@{} 'mysql -u {} -p{} {} -e "
                        "\"use cbioportal; "
                        "select * "
                        "from type_of_cancer;\"'".format(key,
                                                         cbioportal_url,
                                                         user,
                                                         password,
                                                         border), verb)
        logger.info('TYPE OF CANCER with keywords, name, descriptions, e.t.c. in the cBioPortal mysql database: %s' % out)

    if query_gp:
        out = get_shell("ssh {} debian@{} 'mysql -u root -p{} {} -e "
                        "\"use cbioportal; "
                        "select STABLE_ID, DESCRIPTION "
                        "from gene_panel;\"'".format(key,
                                                     cbioportal_url,
                                                     user,
                                                     password,
                                                     border), verb)
        logger.info('GENE PANELS with descriptions in the cBioPortal mysql database: %s' % out)

def main(args):
    logger = configure_logger(logging.getLogger(__name__), args.log_path, args.debug, args.verbose)
    [user, password] = retrieve_auth(args.key, args.url, logger)

    if args.gene_panel or args.type_of_cancer:
        query_portal(args.key, args.url, user, password, args.type_of_cancer, args.gene_panel, args.border, logger)
    else:
        logger.error('Arguments -g/--gene-panel and/or -t/--type-of-cancer are required.')
        sys.exit(1)
