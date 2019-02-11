__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import argparse
import subprocess
import os

import re
import numpy as np

import helper

# Define important constants
REFERENCE_FASTA = "/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa "

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
    required.add_argument("-m", "--mutation-data",
                          help="Command Line Input, the profile_name and profile_description in semi-colon separated "
                               "values. Input needs to be wrapped with ''. e.g. -c 'Mutations (Colorectal);Mutation "
                               "data from whole exome sequencing.'",
                          metavar='STRING')
    required.add_argument("-c", "--caller",
                          choices=helper.caller_choices,
                          help="The caller from which the mutation data is being created from. Choices: ["
                               " | ".join(helper.caller_choices) + "]",
                          metavar='CALLER_NAME',
                          default='.')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Makes program verbose")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="Forces overwriting of data_cancer_type.txt file and *.maf files.")
    # Still need to collect the name and the description
    return parser


def decompress_to_temp():
    # Decompresses each file in the current folder to ../temp/ if it is compressed. otherwise, copy it over
    for file in os.listdir("."):
        file = os.path.abspath(file)
        temp_folder = os.path.abspath('../temp/')
        helper.make_folder(temp_folder)
        if file.endswith(".tar.gz"):
            subprocess.call("tar -xzf {} -C {}".format(file, temp_folder), shell=True)
        elif file.endswith('.gz'):
            subprocess.call("gunzip -c {} > {}/{}".format(file,
                                                          temp_folder,
                                                          os.path.splitext(os.path.basename(file))[0]),
                            shell=True)
        else:
            subprocess.call("cp {} {}".format(file, temp_folder), shell=True)


def copy_mutation_data(input_folder, output_folder):
    subprocess.call('cp -r {} {}'.format(input_folder, output_folder), shell=True)


def export2maf(files_tumors_normals, args):
    # Load Modules
    subprocess.call("module use /oicr/local/analysis/Modules/modulefiles /.mounts/labs/PDE/Modules/modulefiles",
                    shell=True)
    subprocess.call("module load vep/92 vcf2maf python-gsi/3.6.4", shell=True)
    if args.force:
        write = True
    else:
        write = False
    # Get all legitimate files

    for i in range(len(files_tumors_normals)):
        # Figure out if the .maf file should be generated
        vcf = files_tumors_normals[i][0]
        try:
            os.stat(os.path.basename(vcf) + '.maf')
            if not args.force:
                write = False
        except OSError:
            write = True

        # Split for tumor and normal?
        if write:
                subprocess.call('vcf2maf.pl  --input-vcf ' + vcf + '\
                                --output-maf {}/case_lists/{}.maf'.format(args.study_output_folder,
                                                               os.path.splitext(os.path.basename(vcf))[0]) + ' \
                                --normal-id ' + files_tumors_normals[i][1] + '\
                                --tumor-id ' + files_tumors_normals[i][0] + ' \
                                --ref-fasta /.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa vcf2maf.pl \
                                --filter-vcf /.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz \
                                --vep-path $VEP_PATH \
                                --vep-data $VEP_DATA \
                                --species homo_sapiens',
                                shell=True)
        os.remove(vcf)


def add_unmatched_GATK():
    for each in os.listdir('.'):
        # Add unmatched column to files
        pre_process_vcf_GATK(each, each)


def pre_process_vcf_GATK(input_file, output_file):
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


def gather_files_mutect(mutect_type):
    # Check if files have a filtered/sorted version, otherwise get the regular version
    files = os.listdir('.')
    gathered_files = []

    for each in files:
        verified_file = False
        with open(each, 'r') as f:
            tumor_id, normal_id = ['', '']
            for read in f:
                if '##source=mutect' in read:
                    # Ensure the source is MuTect
                    verified_file = True
                elif '##inputs=' in read:
                    # Get the patient and sample ID
                    read.replace('##inputs=', '').split(' ')
                    normal_id, tumor_id = np.array([x.split(':') for x in read])[:, 1]

                    # If the file is a filtered/sorted file remove it if you want unfiltered files
                    if mutect_type == 'unfiltered':
                        if '.filter' in normal_id and '.filter' in tumor_id:
                            verified_file = False
                    elif mutect_type == 'filtered':
                        if not('.filter' in normal_id and '.filter' in tumor_id):
                            verified_file = False
                    # Don't need to read the entire file
                    break
        # Do NOT append the file if it is unverified for any reason.
        if verified_file:
            gathered_files.append([each, tumor_id, normal_id])
    return np.array(gathered_files)


def gather_files_mutect2():
    # Check if files have a filtered/sorted version, otherwise get the regular version
    files = os.listdir('.')
    gathered_files = []
    tumor_only = re.compile('tumor_only')

    for each in files:
        verified_file = False
        with open(each, 'r') as f:
            tumor_id, normal_id = ['', '']
            for read in f:
                # Ensure the source is MuTect
                if '##GATKCommandLine.MuTect2' in read:
                    verified_file = True
                elif '##SAMPLE=<ID=NORMAL,SampleName=' in read:
                    normal_id = read.replace('##SAMPLE=<ID=NORMAL,SampleName=', '').split(',')[0]
                elif '##SAMPLE=<ID=TUMOR,SampleName=' in read:
                    tumor_id = read.replace('##SAMPLE=<ID=TUMOR,SampleName=', '').split(',')[0]

                # BREAK CONDITIONS
                # Don't need to read the entire file if we've found what we need
                if all([normal_id, tumor_id]):
                    break
                # This implies a tumor only MuTect2 file which we don't want?
                elif tumor_only.findall(read):
                    verified_file = False
                    break
        # Do NOT append the file if it is unverified for any reason.
        if verified_file:
            gathered_files.append([each, tumor_id, normal_id])
    return np.array(gathered_files)


def gather_files_strelka():
    files = os.listdir('.')
    gathered_files = []

    for each in files:
        verified_file = False
        flag = False
        tumor_id, normal_id = ['', '']

        with open(each, 'r') as f:
            for read in f:
                if '##source=strelka' in read:
                    # Ensure the source is Strelka
                    verified_file = True
                elif '##content=strelka somatic indel calls'in read:
                    flag = 'indel'
                elif '##content=strelka somatic snv calls' in read:
                    flag = 'snvs'
                elif '##inputs=' in read:
                    # Get the patient and sample ID
                    read = read.strip().replace('##inputs=', '').split(' ')
                    normal_id, tumor_id = np.array([x.split(':') for x in read])[:, 1]
                    # Don't need to read the entire file
                    break
            # Do NOT append the file if it is unverified for any reason.
            if verified_file:
                os.rename(each, '{}.{}.vcf'.format(normal_id, flag))
                gathered_files.append(['{}.{}.vcf'.format(normal_id, flag), tumor_id, normal_id])

    return np.array(gathered_files)


def concat_files_strelka(files_and_more):
    body = []
    # I can do this only because of the renaming that I did previously. This still seems unsafe
    # TODO:: Make this safe by checking ID too
    for each in files_and_more[:, 0]:
        f = open(each, 'r')
        li = f.readlines()
        if '##content=strelka somatic indel calls\n' in li:
            index = max(loc for loc, val in enumerate(li) if '#' in val) + 1
            body = li[index:]
            f.close()
            os.remove(each)
        if '##content=strelka somatic snv calls\n' in li:
            f.close()
            f = open(each, 'a')
            f.writelines(body)
            f.close()

    # Remove removed files
    files_and_more = list(files_and_more)
    new_files = os.listdir('.')
    for i in range(len(files_and_more)-1, 0, -1):
        if not files_and_more[i][0] == new_files:
            del files_and_more[i]
    return np.array(files_and_more)


def save_meta_mutation(args):
    # Generating the meta file is almost as important
    f = open(meta_mutations, 'w+')
    f.write('cancer_study_identifier: {}\n'.format(args.study_id))
    f.write('genetic_alteration_type: MUTATION_EXTENDED\n')
    f.write('datatype: MAF\n')
    f.write('stable_id: mutations\n')
    f.write('show_profile_in_analysis_tab: true\n')
    f.write('profile_name: {}\n'.format(args.mutation_data.split(';')[0]))
    f.write('profile_description: {}\n'.format(args.mutation_data.split(';')[1]))
    f.write('datatype: MAF\n')
    f.write('data_filename: data_mutations_extended.maf\n')
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
