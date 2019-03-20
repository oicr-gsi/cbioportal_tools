__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import shutil
import subprocess

from lib.support import Config

extensionChoices = ["vcf", "maf"]
c_choices = [".tar.gz", ".gz", ".zip"]


def stars():
    # Prints a row of stars
    for a in range(100):
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

def parallel_call(command: str, verb):
    working_on(verb, message=command)
    return subprocess.Popen(command, shell=True)


def decompress_to_temp(mutate_config: Config.Config, study_config: Config.Config, verb):
    # Decompresses each file in the current folder to ../temp_vcf/ if it is compressed. otherwise, copy it over
    if mutate_config.type_config == 'MAF':
        temp = get_temp_folder(study_config.config_map['output_folder'], 'vcf')
    else:
        temp = get_temp_folder(study_config.config_map['output_folder'], mutate_config.type_config.lower())

    working_on(verb, message='Extracting/copying to {}'.format(temp))
    clean_folder(temp)

    for i in range(len(mutate_config.data_frame['FILE_NAME'])):
        input_file =  os.path.abspath(os.path.join(mutate_config.config_map['input_folder'],
                                                   mutate_config.data_frame['FILE_NAME'][i]))

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
