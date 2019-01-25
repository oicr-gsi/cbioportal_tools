import argparse
import subprocess
import os

REFERENCE_FASTA = "/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa"
MUTATION_DATA_META = "MUTATION_EXTENDED"
workflowChoices = ['GATKHaplotypeCaller', 'Mutect', 'Mutect2', 'Strelka']
extensionChoices = ["vcf", "maf"]
compressedChoices = [".tar.gz", ".gz", ".zip"]


def file_choices(choices, fname, parser):
    ext = fname.split('.')
    if bool(set(ext) & set(choices)):
        ext = list(set(ext) & set(choices))[0]
        return fname, ext
    else:
        parser.error("file doesn't end with one of {}".format(choices))
    return fname


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

    parser.add_argument("-d", "--defaults", action="store_true")

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
    out = os.path.basename(input_file)
    input_file = out + extension
    if input_file.endswith(tuple(compressedChoices)):
        decompress(input_file)

    # Begin converting mutation data to legible format
    # I have concerns that this may not work as it is still untested
    subprocess.call("module use /oicr/local/analysis/Modules/modulefiles /.mounts/labs/PDE/Modules/modulefiles")
    subprocess.call("module load vep/92")
    if extension == "vcf":
        subprocess.call("module load vcf2maf")
        subprocess.call("vcf2maf.pl --input-vcf " + input_file +
                        " --output-maf " + out + ".maf" +
                        " --ref-fasta " + REFERENCE_FASTA)
    elif extension == "maf":
        subprocess.call("module load maf2maf")
        subprocess.call("maf2maf.pl --input-maf " + input_file +
                        " --output-maf " + out + ".maf" +
                        " --ref-fasta " + REFERENCE_FASTA)



def generate_study_space(CANCER_STUDY_IDENTIFIER="default"):
    try:
        os.stat(CANCER_STUDY_IDENTIFIER+"/")
    except:
        os.mkdir(CANCER_STUDY_IDENTIFIER)


def generate_metadata(meta_type, parser,
                      CANCER_STUDY_IDENTIFIER=None, GENETIC_ALTERATION_TYPE=None, DATATYPE=None, STABLE_ID=None,
                      SHOW_PROFILE_IN_ANALYSIS_TAB=None, PROFILE_DESCRIPTION=None, PROFILE_NAME=None,
                      DATA_FILENAME=None):
    print("The meta file needs to be generated, adding the tag -d or --default "
          "sets all parts of the file to the defaults")

    print("THIS IS WHERE I NEED TO FIGURE OUT THE CANCER STUDY IDENTIFIER")

    if GENETIC_ALTERATION_TYPE == DATATYPE == STABLE_ID == SHOW_PROFILE_IN_ANALYSIS_TAB == \
            PROFILE_DESCRIPTION == PROFILE_NAME == DATA_FILENAME:
        if meta_type == MUTATION_DATA_META:
            CANCER_STUDY_IDENTIFIER = "default"
            GENETIC_ALTERATION_TYPE = MUTATION_DATA_META
            print parser.parse_args().inputFile
            DATATYPE = parser.parse_args().inputFile[1].upper()  # accessing user input data, structure, list of size 2
            STABLE_ID = "mutations"
            SHOW_PROFILE_IN_ANALYSIS_TAB = "true"
            PROFILE_DESCRIPTION = "Mutation data, more detail can be added here"
            PROFILE_NAME = "Mutations"
            DATA_FILENAME = parser.parse_args().inputFile[0]

    out = os.path.basename(DATA_FILENAME) + ".txt"
    file_out = open(CANCER_STUDY_IDENTIFIER + "/meta_mutations_extended.txt", "w+")
    file_out.write("cancer_study_identifier: " + CANCER_STUDY_IDENTIFIER + "\n")
    file_out.write("genetic_alteration_type: " + GENETIC_ALTERATION_TYPE + "\n")
    file_out.write("datatype: " + DATATYPE + "\n")
    file_out.write("stable_id: " + STABLE_ID + "\n")
    file_out.write("show_profile_in_analysis_tab: " + SHOW_PROFILE_IN_ANALYSIS_TAB + "\n")
    file_out.write("profile_description: " + PROFILE_DESCRIPTION + "\n")
    file_out.write("profile_name: " + PROFILE_NAME + "\n")
    file_out.write("data_filename: " + DATA_FILENAME + "\n")


def main():
    parser = define_parser()
    check_input(parser)
    preprocess_files(parser)
    generate_study_space()
    generate_metadata(MUTATION_DATA_META, parser)


if __name__ == '__main__':
    main()
