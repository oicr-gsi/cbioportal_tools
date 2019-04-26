__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import argparse

from ..support.helper import stars, working_on, get_shell

def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal SQL Query Script.")

    # INTERACTION
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL',
                        required=True)
    parser.add_argument("-p", "--password",
                        help="mySQL Password.",
                        metavar='PASSWORD',
                        required=True)
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


def query_portal(key: str, cbioportal_url: str, password: str, query_toc: bool, query_gp: bool, border, verb):
    if not key == '':
        key = '-i ' + key

    if border:
        border = '-B'
    else:
        border = ''

    if query_toc:
        stars()
        out = get_shell("ssh {} debian@{} 'mysql -u root -p{} {} -e "
                        "\"use cbioportal; "
                        "select * "
                        "from type_of_cancer;\"'".format(key,
                                                         cbioportal_url,
                                                         password,
                                                         border), verb)
        print('TYPE OF CANCER with keywords, name, descriptions, e.t.c. in the cBioPortal mysql database')
        stars()
        print(out)
        stars()

    if query_gp:
        stars()
        out = get_shell("ssh {} debian@{} 'mysql -u root -p{} {} -e "
                        "\"use cbioportal; "
                        "select STABLE_ID, DESCRIPTION "
                        "from gene_panel;\"'".format(key,
                                                     cbioportal_url,
                                                     password,
                                                     border), verb)
        print('GENE PANELS with descriptions in the cBioPortal mysql database')
        stars()
        print(out)
        stars()

    working_on(verb)


def main(args):
    if args.gene_panel or args.type_of_cancer:
        query_portal(args.key, args.url, args.password, args.type_of_cancer, args.gene_panel, args.border, True)
    else:
        print('ERROR:: Arguments -g/--gene-panel and/or -t/--type-of-cancer are required.')
