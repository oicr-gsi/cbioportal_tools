__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import shutil


caller_choices = ['GATKHaplotype', 'Mutect', 'Mutect2', 'Strelka', 'MutectStrelka']
extensionChoices = ["vcf", "maf"]
c_choices = [".tar.gz", ".gz", ".zip"]


def stars():
    # Prints a row of stars
    for a in range(30):
        print('*', end="")
    print('')


def change_folder(folder):
    # Try to safely change working directory
    original_working_directory = os.getcwd()
    try:
        os.chdir(folder)
    except OSError:
        stars()
        print('The path to your folder probably does not exist. Trying to make the folder for you.')
        stars()
        try:
            os.mkdir(folder)
            os.chdir(folder)
        except OSError:
            stars()
            raise ValueError('You may not have permission to create folders there. Very sad')
    return original_working_directory


def make_folder(path):
    try:
        os.stat(path)
    except OSError:
        os.mkdir(path)


def clean_folder(path):
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


def reset_folder(owd):
    os.chdir(owd)
    # Go to original working directory, needs to be used in junction to stored variable


def working_on(verbosity, message='Success!\n'):
    # Method is for verbose option. Prints Success if no parameter specified
    if verbosity:
        print(message)


def write_tsv_dataframe(name, dataset):
    dataset.to_csv(name, sep='\t', index=False)


def get_temp_folder(input_folder, ext):
    return os.path.abspath(os.path.join(input_folder, '../temp_{}/'.format(ext)))
