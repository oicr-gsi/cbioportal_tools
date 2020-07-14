#! /usr/bin/env python3

"""Main script to run the Janus tools"""

# Python library imports
import argparse
import logging
import sys

# Janus tools
from generate import generator
from query import query
from remove import remove
from upload import importer


def super_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='janus.py: A toolkit for cBioPortal interaction. '+\
                    'For more usage, examples and documentation see https://github.com/oicr-gsi/cbioportal_tools')
    parser.add_argument('--debug', action='store_true', help="Even more verbose logging")
    parser.add_argument('--verbose', action='store_true', help="More verbose logging")
    parser.add_argument('-l', '--log-path', metavar='PATH', help='Path of file where '+\
                        'log output will be appended. Optional, defaults to STDERR.')

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
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.which == 'generator':
        generator.main(args)
    elif args.which == 'import':
        importer.main(args)
    elif args.which == 'remove':
        remove.main(args)
    elif args.which == 'query':
        query.main(args)

if __name__ == '__main__':
    main()
