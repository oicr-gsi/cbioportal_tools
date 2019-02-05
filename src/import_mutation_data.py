import argparse
import subprocess
import os

import helper

# Define important constants
REFERENCE_FASTA = "/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa"
MUTATION_DATA_META = "MUTATION_EXTENDED"
workflowChoices = ['GATKHaplotypeCaller', 'Mutect', 'Mutect2', 'Strelka']



def define_parser():
    # Define program arguments
    parser = argparse.ArgumentParser(description="cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a "
                                                 "command line tool for extracting data from files generated through "
                                                 "the seqware workflows, as well as from tools run outside of the "
                                                 "pipeline, and put them into the correct cBioPortal import files "
                                                 "(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).")

    required = parser.add_argument_group('Required Arguments')
    required.add_argument("-i", "--study-input-folder",
                          type=lambda folder: helper.check_files_in_folder(helper.extensionChoices, folder, parser),
                          help="The input folder can contain compressed: [" +
                               " | ".join(helper.compressedChoices) + "] "
                                                                      " or uncompressed format in: [" +
                               " | ".join(helper.extensionChoices) + "] ",
                          default='.',
                          metavar='FOLDER')
    parser.add_argument("-d", "--default",
                        action="store_true",
                        help="Prevents need for user input by trying to parse study ID, you must follow format "
                             "indicated in the help if you use this. **This tag is not recommended and cannot be used "
                             "alongside -c as -c takes precedence.")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    parser.add_argument("--force-vcf2maf",
                        action="store_true",
                        help="Forces overwriting of files converted from vcf to maf.")
    # Still need to collect the name and the description
    return parser


def decompress(input_file):
    # Decompresses file if it is compressed
    if input_file.endswith(".tar.gz"):
        subprocess.call("gunzip -c " + input_file + " | tar xopf -")
    elif input_file.endswith(".gz"):
        subprocess.call("tar xopf " + input_file)
    elif input_file.endswith(".zip"):
        subprocess.call("unzip -a " + input_file)


def pre_process_files(args):
    input_file, extension = args.inputFile
    out = os.path.basename(input_file)
    input_file = out + extension  # Hmmm, not super sure if what I'm doing here makes any sense
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


def main():
    import main_minimal
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_cancer_(args, verb)


'''
vcf2maf.pl  --input-vcf merpi.vcf \
            --output-maf ../GATKMAF/GECCO_0001_Li_R_TS.g.maf \
            --tumor-id GECCO_0001_Li_R_TS.g \
            --normal-id GECCO_0001_Ly_P_TS.g \
            --ref-fasta /.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.favcf2maf.pl \
            --filter-vcf ../../reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz \
            --vep-path $VEP_PATH \
            --vep-data $VEP_DATA \
            --species homo_sapiens
'''
if __name__ == '__main__':
    main()
