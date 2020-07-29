"""General utility functions"""

# TODO replace these with cleaner alternatives where possible, eg. excluding shell calls

import logging
import os
import shutil
import subprocess
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


def exit_program(message='', code=1):
    print(message)
    exit(code)


def clean_folder(path,force):
    if os.path.exists(path):
        if force:
            shutil.rmtree(path)
            make_folder(path)
        else:
            print('The following path will be removed and overwritten : {}'.format(path))
            ## ask for a response, get the first character in lowercase
            response=input("Press y to continue, any other key to exit:").lower().strip()[:1]
            try:
                if response == 'y':
                    shutil.rmtree(path)
                    make_folder(path)
                else:
                    print('Exiting Janus')
                    exit()
                    ### trying to handle ctrl-c butthis doesnt seem to be working
            except KeyboardInterrupt:
                print('Exiting Janus')
                exit()
    else:
        make_folder(path)

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
    # TODO refactor to use Python tar & gzip libraries instead of shell calls
    # Decompresses each file in the current folder to ../temp_vcf/ if it is compressed. otherwise, copy it over
    if mutate_config.type_config == 'MAF':
        temp = get_temp_folder(study_config.config_map['output_folder'], 'vcf')
    else:
        temp = get_temp_folder(study_config.config_map['output_folder'], mutate_config.datahandler.lower())

    working_on(verb, message='Extracting/copying to {}'.format(temp))
    clean_folder(temp,True)

    for i in range(len(mutate_config.data_frame['FILE_NAME'])):
        input_file =  os.path.abspath(os.path.join(mutate_config.config_map['input_folder'],
                                                   mutate_config.data_frame['FILE_NAME'][i]))
        print(input_file)
        if not os.path.isfile(input_file):
            raise FileNotFoundError('The path to the file you have provided is not correct ...\n' + input_file)

        output_file = os.path.abspath(os.path.join(temp, mutate_config.data_frame['FILE_NAME'][i]))

        if input_file.endswith(".tar.gz"):
            call_shell("tar -xzf {} -C {}".format(input_file, temp), verb)

            mutate_config.data_frame['FILE_NAME'][i] = mutate_config.data_frame['FILE_NAME'][i].strip('.tar.gz')

        elif input_file.endswith('.gz'):
            call_shell("zcat {} > {}".format(input_file, output_file.strip('.gz')), verb)

            mutate_config.data_frame['FILE_NAME'][i] = mutate_config.data_frame['FILE_NAME'][i].strip('.gz')

        else:
            call_shell("cp {} {}".format(input_file, output_file), verb)

    mutate_config.config_map['input_folder'] = temp


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

