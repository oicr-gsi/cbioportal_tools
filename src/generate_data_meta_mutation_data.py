__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import argparse
import subprocess
import os

import re

import helper

# Define important constants
REFERENCE_FASTA = "/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa"

meta_mutations = 'meta_mutations.txt'
data_mutations = 'data_mutations.txt'


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
    required.add_argument("-o", "--study-output-folder",
                          help="The folder you want to export this generated data_samples.txt file to. Generally this "
                               "will be the main folder of the study being generated. If left blank this will generate "
                               "it wherever you run the script from.",
                          metavar='FOLDER',
                          default='.')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Forces overwriting of data_cancer_type.txt file and *.maf files.")
    # Still need to collect the name and the description
    return parser


def pre_process_vcf_unmatched(input_file, output_file):
    i = open(input_file, 'r')
    o = open(output_file, 'w')
    while True:
        line = i.readline()
        if '\t' in line:
            break
        else:
            o.write(line)
    o.write(i.readline() + '\tUNMATCHED')
    while True:
        line = i.readline().split('\t')
        index = len(line) - 1
        write = '\t'.join([*line, line[index]])
        if index < 2:
            break
        else:
            o.write(write)
    i.close()
    o.close()


def decompress():
    # Decompresses each file in the current folder to ../temp/ if it is compressed. otherwise, copy it over
    for file in os.listdir("."):
        helper.make_folder("../temp/")
        if file.endswith(".tar.gz"):
            subprocess.call("tar -xzf " + file + " -C ../temp/")
        else:
            subprocess.call("cp " + file + " ../temp/")


def add_unmatched():
    for each in os.listdir():
        # Add unmatched column to files
        pre_process_vcf_unmatched(each, each)


def export2maf(args):
    # Load Modules
    reg_norms = re.compile('GECCO_[0-9]{4}_Li_P')
    reg_tumor = re.compile('GECCO_[0-9]{4}_Ly_R')
    subprocess.call("module use /oicr/local/analysis/Modules/modulefiles /.mounts/labs/PDE/Modules/modulefiles")
    subprocess.call("module load vep/92 vcf2maf")
    # Get all files ending in .vcf
    for vcf in [x for x in os.listdir('.') if x.endswith('.vcf')]:
        # Figure out if the .maf file should be generated
        if args.force:
            write = True
        try:
            os.stat(os.path.basename(vcf) + '.maf')
            if not args.force:
                write = False
        except OSError:
            write = True

        # Split for tumor and normal?
        if write:
            if len(reg_tumor.findall(vcf)) > 0:
                os.call('vcf2maf.pl  --input-vcf ' + vcf + '\
                        --output-maf ../GATKMAF/' + os.path.basename(vcf)+'.maf \
                        --tumor-id ' + reg_tumor.findall(vcf)[0] + ' \
                        --ref-fasta /.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.favcf2maf.pl \
                        --filter-vcf /.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz \
                        --vep-path $VEP_PATH \
                        --vep-data $VEP_DATA \
                        --species homo_sapiens')
            elif len(reg_norms.findall(vcf)) > 0:
                os.call('vcf2maf.pl  --input-vcf ' + vcf + '\
                        --output-maf ../GATKMAF/' + os.path.basename(vcf)+'.maf \
                        --normal-id ' + reg_norms.findall(vcf)[0] + ' \
                        --ref-fasta /.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.favcf2maf.pl \
                        --filter-vcf /.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz \
                        --vep-path $VEP_PATH \
                        --vep-data $VEP_DATA \
                        --species homo_sapiens')
        os.remove(vcf)


def copy_mutation_data(input_folder, output_folder):
    os.call('cp -r ' + input_folder + ' ' + output_folder)


def save_meta_mutation(args):
    # Generating the meta file is almost as important
    f = open(meta_mutations, 'w+')
    f.write('cancer_study_identifier: {}\n'.format(args.study_id))
    f.write('genetic_alteration_type: MUTATION_EXTENDED\n')
    f.write('datatype: MAF\n')
    f.write('stable_id: mutations\n')
    f.write('show_profile_in_analysis_tab: true\n')
    f.write('profile_name: {}\n'.format(args.profile_name))
    f.write('profile_description: {}\n'.format(args.profile_description))
    f.write('datatype: MAF\n')
    f.write('data_filename: {}\n'.format(args.study_id + '.maf'))
    # This part ^^^ will be wrong until I understand what exactly and extended maf file is and how to make it
    f.close()


def main():
    import main_minimal
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_mutation_meta_data(args, verb)
    # Import mutation data from .vcf 2 .maf
    # Pre-process files first by adding unmatched coloumn
    # Apply vcf2maf command on each depending on name:
    #       Ly_R are normals
    #       Li_P are tumour


if __name__ == '__main__':
    main()
