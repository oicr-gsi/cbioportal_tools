import argparse
import subprocess


def file_choices(choices, fname, parser):
    ext = fname.split('.')
    if bool(set(ext) & set(choices)):
        ext = list(set(ext) & set(choices))
        return fname, ext
    else:
        parser.error("file doesn't end with one of {}".format(choices))
    return fname


workflowChoices = ['GATKHaplotypeCaller', 'Mutect', 'Mutect2', 'Strelka']
extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]


def define_parser():
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through the "
                                                 "seqware workflows, as well as from tools run outside of the pipeline, "
                                                 "and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")

    parser.add_argument("inputFile",
                        type=lambda s: file_choices(extensionChoices, s, parser),
                        help="The input file, can be of compressed: " +
                             " | ".join(compressedChoices) + "] "
                             " or uncompressed format in: [" +
                             " | ".join(extensionChoices) + "] "
                             "If the file is compressed, optional tag -c must be added")

    ######### OPTIONAL ARGUMENTS ###########
    reqArg = parser.add_argument_group('required arguments')

    reqArg.add_argument("-c", "--compressed",
                        help="If the input file is compressed this tag must be added",
                        action="store_true")

    reqArg.add_argument("-w", "--workflowUsed",
                        help="The workflow used is a mandatory tag, choices are: [" + " | ".join(workflowChoices) + "]",
                        choices=workflowChoices,
                        metavar='',
                        default='')
    return parser


def check_input(parser):
    arguments = parser.parse_args()
    input_file, extension = arguments.inputFile
    if (input_file[len(input_file) - 1] not in extensionChoices) and not arguments.compressed:
        print ("Compressed tag was not specified, please do that next time")
        arguments.compressed = True

    if arguments.workflowUsed not in workflowChoices:
        parser.error("Either no workflow has been specified, or there has been a misspelling."
                     "\n Choices are: [" + " | ".join(workflowChoices) + "]")


def decompress(input_file):
    if input_file.endswith(".tar.gz"):
        subprocess.call("gunzip -c " + input_file + " | tar xopf -")
    elif input_file.endswith(".gz"):
        subprocess.call("tar xopf " + input_file)
    elif input_file.endswith(".zip"):
        subprocess.call("unzip -a " + input_file)


def preprocess_files(parser):
    input_file, extension = parser.parse_args().inputFile
    if input_file.endswith(compressedChoices):
        decompress(input_file)
    if extension == "vcf":
        subprocess.call("module use /oicr/local/analysis/Modules/modulefiles /.mounts/labs/PDE/Modules/modulefiles")
        subprocess.call("module load vcf2maf; module load vep/92")


def main():
    parser = define_parser()
    check_input(parser)
    preprocess_files(parser)


if __name__ == '__main__':
    main()
