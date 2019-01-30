import os


def stars():
    # Prints a row of stars
    for a in range(30):
        print'*',


def change_folder(folder):
    # Try to safely change working directory
    original_working_directory = os.getcwd()
    try:
        os.chdir(folder)
    except OSError:
        stars()
        print 'The path to your folder probably does not exist. Trying to make the folder for you.'
        stars()
        try:
            os.mkdir(folder)
        except OSError:
            stars()
            raise ValueError('You may not have permission to create folders there. Very sad')
    return original_working_directory


def reset_folder(owd):
    os.chdir(owd)
    # Go to original working directory, needs to be used in junction to stored variable


def working_on(verbosity, message='Success!'):
    # Method is for verbose option. Prints Success if no parameter specified
    if verbosity:
        print message