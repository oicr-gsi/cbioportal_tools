#! /usr/bin/env python3

"""Main script to run the Janus tools"""

# Command Line Imports
import argparse
import sys

# Other Scripts
from lib.tools import remove, importer, query, generator


def super_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='janus.py a set of cBioPortal interaction tools. '
                    'Janus is a wrapper-like utility for managing cBioPortal studies and your instance, each sub-tool '
                    'functions on it\'s own. '
                    'For more usage, examples and documentation see https://github.com/oicr-gsi/cbioportal_tools')
    subparsers = parser.add_subparsers(title='Janus a set of cBioPortal Tools',
                                       description='Current set of tools',
                                       dest='which')

    subparsers.add_parser('generator',
                          add_help=False,
                          parents=[generator.define_parser()],
                          help='Generator Functions for generating whole studies from data pipelines. '
                               'Will require configuration of study configuration files')
    subparsers.add_parser('import',
                          add_help=False,
                          parents=[importer.define_parser()],
                          help='Importer for complete studies or gene_panels. Requires a cBioPortal '
                               'ready study or a complete gene_panel')
    subparsers.add_parser('remove',
                          add_help=False,
                          parents=[remove.define_parser()],
                          help='Removal tool for studies. Requires study_id of particular study')
    subparsers.add_parser('query',
                          add_help=False,
                          parents=[query.define_parser()],
                          help='Query tool for gene_panels and cancer_type. Requires password to root MySQL user')

    return parser


def main():
    parser = super_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()

    if   args.which == 'generator':
        generator.main(args)
    elif args.which == 'import':
        importer.main(args)
    elif args.which == 'remove':
        remove.main(args)
    elif args.which == 'query':
        query.main(args)

if __name__ == '__main__':
    main()
