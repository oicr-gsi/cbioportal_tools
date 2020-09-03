#! /usr/bin/env python3

"""Main script to run the Janus tools"""

import argparse
import logging
import sys

from utilities.main import main

def super_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='janus: A cBioPortal gateway')
    parser.add_argument('--debug', action='store_true', help="Even more verbose logging")
    parser.add_argument('--verbose', action='store_true', help="More verbose logging")
    parser.add_argument('-l', '--log-path', metavar='PATH', help='Path of file where '+\
                        'log output will be appended. Optional, defaults to STDERR.')
    subparsers = parser.add_subparsers(title='Janus subcommands',
                                       dest='which')
    add_generation_arguments(
        subparsers.add_parser('generate',
                              help='Generate cBioPortal study from pipeline data. Requires '+\
                              'appropriate Janus configuration files.')
    )
    add_validation_arguments(
        subparsers.add_parser('validate',
                              help='Validate a Janus configuration file against a schema.')
    )
    return parser

def add_generation_arguments(parser):
    required = parser.add_argument_group('Required arguments')

    required.add_argument("-c", "--config", help="Path to study config file",
                          metavar='PATH', required=True)
    required.add_argument("-o", "--out", help="Directory for study output",
                          metavar='PATH', required=True)
    optional = parser.add_argument_group('Optional arguments')
    optional.add_argument("-d", "--dry-run",
                          action="store_true",
                          help="Dry-run mode; write sample, patient, and metadata files, but "+\
                          "do not process pipeline data. Used for rapid testing and sanity-checking.")
    optional.add_argument("-f", "--force",
                          action="store_true",
                          help="Force overwrite of output folder; delete previous contents, if any.")

def add_validation_arguments(parser):
    parser.add_argument("-c", "--config", help="Path to Janus config file",
                        metavar='PATH', required=True)
    parser.add_argument("-s", "--schema", help="Path to Janus schema file",
                        metavar='PATH', required=True)

if __name__ == '__main__':
    parser = super_parser()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    main(parser.parse_args())
