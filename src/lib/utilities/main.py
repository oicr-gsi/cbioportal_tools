"""Front-end method for launching Janus functions"""

import logging
import sys
from generate.study import study
from utilities.config import config
from utilities.schema import schema

def main(args):
    # process logging args from top-level argument parser
    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARN
    log_path = getattr(args, 'log_path', None)

    # run appropriate sub-function    
    if args.which == 'generate':
        study(args.config, log_level, log_path).write_all(args.out, args.dry_run, args.force)
    elif args.which == 'template':
        if args.out=='-':
            out_file = sys.stdout
        else:
            out_file = open(args.out, 'w')
        schema(args.schema, log_level).write_template(out_file, args.describe)
        if args.out!='-':
            out_file.close()
    elif args.which == 'validate':
        valid = config(args.config, args.schema, log_level, log_path=log_path).validate_syntax()
        if not valid:
            print("Configuration is not valid", file=sys.stderr)
            exit(1)
    else:
        print("Invalid command mode %s" % args.which, file=sys.stderr)
        exit(1)
