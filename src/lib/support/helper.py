"""General utility functions"""

# TODO replace these with cleaner alternatives where possible, eg. excluding shell calls

import gzip
import logging
import os
import re
import shutil
import subprocess
import tarfile
import time

from support.Config import Config
from constants.constants import config2name_map, supported_pipe

extensionChoices = ["vcf", "maf"]
c_choices = [".tar.gz", ".gz", ".zip"]

def configure_logger(logger, log_path=None, debug=False, verbose=False):
    """Customize a Logger object with given parameters"""
    #logger = logging.getLogger(__name__)
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
    logger.warning("Call to deprecated helper.stars() method")


def clean_folder(path,force):
    if os.path.exists(path):
        if force:
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            raise OSError("Output path %s exists and --force not in effect; exiting" % path)
    else:
        os.makedirs(path)

def working_on(verbose, message='Success reported via deprecated working_on() method'):
    # Method is for verbose option. Prints Success if no parameter specified
    logger = logging.getLogger(__name__)
    logger = configure_logger(logger, verbose=verbose)
    logger.info(message)


def get_temp_folder(output_folder, ext) -> str:
    return os.path.abspath(os.path.join(output_folder, 'temp/temp_{}/'.format(ext)))


def call_shell(command: str, verb):
    working_on(verb, message=command)
    output = subprocess.call(command, shell=True)
    return output


def get_shell(command: str, verb) -> str:
    working_on(verb, message=command)
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    return output.decode('utf-8')


def parallel_call(command: str, verb):
    working_on(verb, message=command)
    return subprocess.Popen(command, shell=True)


def decompress_to_temp(mutate_config: Config, study_config: Config, verb):
    """Create a temporary directory; extract/decompress/copy input to it; also updates mutate_config"""
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
    # extract, decompress, or copy files
    for name in mutate_config.data_frame['FILE_NAME'].tolist():
        input_path = os.path.abspath(os.path.join(mutate_config.config_map['input_folder'], name))
        err = None
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
            logger.info("Extracting .tar archive %s to %s" % (input_path, temp_dir))
            with tarfile.open(input_path) as tf:
                tf.extractall(temp_dir)
        elif re.search('\.gz$', input_path):
            logger.info("Decompressing .gz file %s to %s" % (input_path, temp_dir))
            dest_name = re.split('\.gz$', os.path.basename(input_path)).pop(0)
            with gzip.open(input_path) as source:
                dest = open(os.path.join(temp_dir, dest_name), 'wb')
                shutil.copyfileobj(source, dest)
                dest.close()
        else:
            logger.info("Copying file %s to %s" % (input_path, temp_dir))
            dest = os.path.join(temp_dir, os.path.basename(input_path))
            shutil.copyfile(input_path, dest)
    # side effect: modify mutate_config to set input folder to the new temp_dir
    # TODO refactor to make this more explicit
    mutate_config.config_map['input_folder'] = temp_dir


def concat_files(exports_config:Config, study_config: Config, verb):
    # TODO refactor to use Python file objects instead of shell calls
    concated_file = os.path.join(study_config.config_map['output_folder'],
                                 'data_{}_concat.txt'.format(config2name_map[exports_config.alterationtype + ":" + exports_config.datahandler]))

    input_folder = exports_config.config_map['input_folder']

    call_shell('head -n 1 {} > {}'.format(os.path.join(input_folder,exports_config.data_frame['FILE_NAME'][0]),
                                          concated_file), verb)

    for each in exports_config.data_frame['FILE_NAME']:
        input_file = os.path.join(input_folder, each)
        # Concat all but first line to remove header.
        call_shell('tail -n +2 {} >> {}'.format(input_file, concated_file), verb)

