#! /usr/bin/env python3

"""Front-end for generation of a cBioPortal import folder"""

import argparse
import logging

from generate.study import study

def define_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="janus: CLI tool to generate an importable study for a cBioPortal instance")
    required = parser.add_argument_group('Required arguments:')

    required.add_argument("-c", "--config", help="Path to study config file",
                        metavar='PATH', required=True)
    required.add_argument("-o", "--out", help="Directory for study output",
                        metavar='PATH', required=True)
    optional = parser.add_argument_group('Optional arguments:')
    optional.add_argument("-d", "--dry-run",
                          action="store_true",
                          help="Dry-run mode; write sample, patient, and metadata files, but "+\
                          "do not process pipeline data. Used for rapid testing and sanity-checking.")
    optional.add_argument("-f", "--force",
                          action="store_true",
                          help="Force overwrite of output folder; delete previous contents, if any.")
    return parser


def main(args):

    # process logging args from top-level argument parser
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    log_path = getattr(args, 'log_path', None)

    study(args.config, log_level, log_path).write_all(args.out, args.dry_run, args.force)
