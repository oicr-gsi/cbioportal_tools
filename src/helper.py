import os


extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]


def stars():
    # Prints a row of stars
    for a in range(30):
        print'*',
    print ''


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


def check_files_in_folder(choices, folder, parser):
    # Checks file extensions within folder for belonging in extensionChoices (important constants)
    for each in os.listdir(folder):
        ext = each.split('.')
        if not (bool(set(ext) & set(choices))):
            parser.error(each + " file doesn't end with one of {}".format(choices))
    return folder


def write_tsv_dataframe(name, dataset):
    dataset.to_csv(name, sep='\t', index=False)
