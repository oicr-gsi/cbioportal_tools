"""General utility functions"""

# TODO replace these with cleaner alternatives where possible, eg. excluding shell calls

import gzip
import logging
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time

from support.Config import Config
from constants.constants import config2name_map

def configure_logger(logger, log_path=None, debug=False, verbose=False):
    """Customize a Logger object with given parameters"""
    # standalone method, for use to configure loggers in the helper module
    if len(logger.handlers) > 0: # remove duplicate handlers from previous get_logger() calls
        logger.handlers.clear()
    log_level = logging.WARN
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    logger.setLevel(log_level)
    handler = None
    if log_path==None:
        handler = logging.StreamHandler()
    else:
        dir_path = os.path.abspath(os.path.join(log_path, os.pardir))
        valid = True
        if not os.path.exists(dir_path):
            sys.stderr.write("ERROR: Log directory %s does not exist.\n" % dir_path)
            valid = False
        elif not os.path.isdir(dir_path):
            sys.stderr.write("ERROR: Log destination %s is not a directory.\n" % dir_path)
            valid = False
        elif not os.access(dir_path, os.W_OK):
            sys.stderr.write("ERROR: Log directory %s is not writable.\n" % dir_path)
            valid = False
        if not valid: sys.exit(1)
        handler = logging.FileHandler(log_path)
    handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s',
                                  datefmt='%Y-%m-%d_%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def stars():
    # Formerly used to print a decorative row of stars
    logger = logging.getLogger(__name__)
    logger = configure_logger(logger, verbose=True)
    logger.warning("Use of deprecated helper.stars() method")

def clean_folder(path,force):
    if os.path.exists(path):
        if force:
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            raise OSError("Output path %s exists and --force not in effect; exiting" % path)
    else:
        os.makedirs(path)

def working_on(verbose, message='Success reported.'):
    logger = logging.getLogger(__name__)
    logger = configure_logger(logger, verbose=verbose)
    logger.warning("Use of deprecated 'working_on' method")
    logger.info("Via deprecated working_on(): "+message)

def get_temp_folder(output_folder, ext) -> str:
    return os.path.abspath(os.path.join(output_folder, 'temp/temp_{}/'.format(ext)))

def decompress_to_temp(mutate_config: Config, study_config: Config, verb):
    logger = configure_logger(logging.getLogger(__name__), verbose=verb)
    logger.warn("Call to deprecated legacy decompress_to_temp method; use relocate_inputs instead")
    return relocate_inputs(mutate_config, study_config, verb)

def relocate_inputs(mutate_config: Config, study_config: Config, verb):
    """Extract/decompress/copy input to a new tempdir; return updated mutate_config"""
    logger = configure_logger(logging.getLogger(__name__), verbose=verb)
    # construct the output directory
    output_folder = study_config.config_map['output_folder']
    if mutate_config.type_config == 'MAF':
        suffix = 'vcf'
    else:
        suffix = mutate_config.datahandler.lower()
    temp_dir = os.path.abspath(os.path.join(output_folder, 'temp/temp_{}/'.format(suffix)))
    if os.path.exists(temp_dir):
        logger.info("Removing existing directory '%s'" % temp_dir)
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    # extract, decompress, or copy files; update filenames in mutate_config
    updated_names = []
    for name in mutate_config.data_frame['FILE_NAME'].tolist():
        input_path = os.path.abspath(os.path.join(mutate_config.config_map['input_folder'], name))
        err = None
        updated_name = name
        if not os.path.exists(input_path):
            err = "Input path '%s' does not exist" % input_path
        elif not os.path.isfile(input_path):
            err = "Input path '%s' exists but is not a file" % input_path
        elif not os.access(input_path, os.R_OK):
            err = "Input file '%s' exists but is not readable" % input_path
        if err:
            logger.error(err)
            raise FileNotFoundError(err)
        if re.search('\.tar(\.gz)?$', input_path) or re.search('\.tgz$', input_path):
            logger.info("Extracting TAR archive %s to %s" % (input_path, temp_dir))
            with tarfile.open(input_path) as tf:
                tf.extractall(temp_dir)
        elif re.search('\.gz$', input_path):
            logger.info("Decompressing .gz file %s to %s" % (input_path, temp_dir))
            dest_name = re.split('\.gz$', os.path.basename(input_path)).pop(0)
            updated_name = dest_name
            with gzip.open(input_path) as source:
                dest = open(os.path.join(temp_dir, dest_name), 'wb')
                shutil.copyfileobj(source, dest)
                dest.close()
        else:
            logger.info("Copying file %s to %s" % (input_path, temp_dir))
            dest = os.path.join(temp_dir, os.path.basename(input_path))
            shutil.copyfile(input_path, dest)
        updated_names.append(updated_name)
    # modify mutate_config to update input folder and changed filenames (if any)
    mutate_config.data_frame['FILE_NAME'] = updated_names
    mutate_config.config_map['input_folder'] = temp_dir
    return mutate_config

def concat_files(exports_config:Config, study_config: Config, verb):
    """Concatenate input files; keep the first (header) line from first file only"""
    logger = configure_logger(logging.getLogger(__name__), verbose=verb)
    input_dir = exports_config.config_map['input_folder']
    output_dir = study_config.config_map['output_folder']
    input_names = exports_config.data_frame['FILE_NAME'].tolist()
    # TODO get rid of unwieldy and error-prone config2name_map
    output_name_key = exports_config.alterationtype + ":" + exports_config.datahandler
    output_name = 'data_{}_concat.txt'.format(config2name_map[output_name_key])
    output_path = os.path.join(output_dir, output_name)
    logger.info("Started writing concatenated output from %s to %s" % (input_dir, output_path))
    output_file = open(output_path, 'w')
    first = True
    for name in input_names:
        logger.debug("Appending contents of %s to output %s" % (name, output_path))
        with open(os.path.join(input_dir, name), 'r') as input_file:
            header = input_file.readline()
            if first:
                output_file.write(header)
                first = False
            # copy from current position (2nd line) to EOF
            shutil.copyfileobj(input_file, output_file)
    output_file.close()
    logger.info("Finished writing concatenated output from %s to %s" % (input_dir, output_path))

