__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "1.0"

import subprocess
import argparse
import os


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal SQL Query Script.")

    # FILES
    parser.add_argument("-P", "--gene-panel-file",
                        help="A formatted gene-panel you would like to upload.",
                        metavar='PANEL')

    # INTERACTION
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL')
    parser.add_argument("-p", "--password",
                        help="mySQL Password.",
                        metavar='PASSWORD')
    parser.add_argument("-k", "--key",
                        help="The location of the cBioPortal Key.",
                        metavar='KEY',
                        default='')

    # QUERY
    parser.add_argument("-t", "--type-of-cancer",
                        help="Query the types of cancer in the cBioPortal Database",
                        action='store_true')
    parser.add_argument("-g", "--query-gene-panel",
                        help="Query the gene-panels in the cBioPortal Database",
                        action='store_true')
    parser.add_argument("-b", "--border",
                        help="Disables borders around the query.",
                        action='store_true',
                        default=False)

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


def get_shell(command: str, verb) -> str:
    working_on(verb, message=command)
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    return output.decode('utf-8')


def import_portal(key: str, cbioportal_url: str, gene_panel, verb):
    if not key == '':
        key = '-i ' + key

    gene_panel = os.path.abspath(gene_panel)

    stars()
    get_shell("scp {} {} debian@{}:/home/debian/gene_panels/{}".format(key, gene_panel, cbioportal_url, os.path.basename(gene_panel)), verb)

    out = get_shell("ssh {} debian@{} '"
                    "source /etc/profile; "
                    "cd ~/cbioportal/core/src/main/scripts; "
                    "./importGenePanel.pl --data ~/gene_panels/{}'".format(key, cbioportal_url, os.path.basename(gene_panel)), verb)
    print('importing cancer type')
    stars()
    if 'exit status 70.' in out:
        print('There is a missing Identifier/Keyword in the gene_panel file. Or it has been mistyped')
    print(out)
    stars()

    working_on(verb)


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

def main():
    args = define_parser().parse_args()
    if args.query_gene_panel or args.type_of_cancer:
        query_portal(args.key, args.url, args.password, args.type_of_cancer, args.query_gene_panel, args.border, True)

    if args.gene_panel_file:
        import_portal(args.key, args.url, args.gene_panel_file, True)


if __name__ == '__main__':
    main()
