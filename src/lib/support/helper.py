import subprocess

__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import shutil

from lib.support import Config

extensionChoices = ["vcf", "maf"]
c_choices = [".tar.gz", ".gz", ".zip"]


def stars():
    # Prints a row of stars
    for a in range(30):
        print('*', end="")
    print('')


def make_folder(path):
    try:
        os.stat(path)
    except OSError:
        os.makedirs(path)


def clean_folder(path):
    print('Please ensure that you are not losing any data in {}'.format(path))
    make_folder(path)
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def working_on(verbosity, message='Success!\n'):
    # Method is for verbose option. Prints Success if no parameter specified
    if verbosity:
        print(message)


def get_temp_folder(output_folder, ext) -> str:
    return os.path.abspath(os.path.join(output_folder, '../temp/temp_{}/'.format(ext)))


def get_cbiowrap_file(study_config: Config.Config, name: str) -> str:
    return os.path.join(get_temp_folder(study_config.config_map['output_folder'], 'study'), name)


def call_shell(command: str, verb):
    working_on(verb, message=command)
    subprocess.call(command, shell=True)