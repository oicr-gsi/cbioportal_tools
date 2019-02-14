__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import argparse
import subprocess
import os
import time

import numpy as np

import helper

# Define important constants
ref_fasta = "/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa "
filter_vcf = '/.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz'

meta_mutations = 'meta_mutations.txt'
data_mutations = 'data_mutations.txt'
data_mutations_extended = 'data_mutations_extended.maf'


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


def decompress_to_temp(args):
    # Decompresses each file in the current folder to ../temp_vcf/ if it is compressed. otherwise, copy it over
    temp_folder = helper.get_temp_folder(args, 'vcf')
    helper.make_folder(temp_folder)
    helper.clean_folder(temp_folder)
    for file in os.listdir('.'):
        file = os.path.abspath(file)
        if file.endswith(".tar.gz"):
            subprocess.call("tar -xzf {} -C {}".format(file, temp_folder), shell=True)
        elif file.endswith('.gz'):
            subprocess.call("zcat {} > {}/{}".format(file,
                                                     temp_folder,
                                                     os.path.splitext(os.path.basename(file))[0]),
                            shell=True)
        else:
            subprocess.call("cp {} {}".format(file, temp_folder), shell=True)


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


## The currently working caller readers


def gather_files_mutect(mutect_type):
    files = os.listdir('.')
    files.sort()
    gathered_files = []

    for each in files:
        verified_file = correct_filter = False
        normal_id = tumor_id = False

        f = open(each, 'r')
        while not all([verified_file, normal_id, tumor_id]):
            read = f.readline()

            if not read.startswith('#'):
                break

            if read.startswith('##source=mutect'):
                # Ensure the source is MuTect
                verified_file = True
            elif read.startswith('##inputs='):
                # Get the patient and sample ID
                read = read.replace('##inputs=', '').strip().split(' ')
                normal_id, tumor_id = np.array([x.split(':') for x in read])[:, 1]
                # If the file is a filtered/sorted file set true
                if 'filter' in normal_id and 'filter' in tumor_id:
                    correct_filter = True
                elif not('filter' in normal_id and 'filter' in tumor_id):
                    correct_filter = False

                # Flip it if it's unfiltered
                if mutect_type == 'unfiltered':
                    correct_filter = not correct_filter
                # Don't need to read the entire file
        # Do NOT append the file if it is unverified for any reason.
        f.close()
        if verified_file and correct_filter:
            os.rename(each, '{}.vcf'.format(normal_id))
            gathered_files.append(['{}.vcf'.format(normal_id), normal_id, tumor_id, normal_id, tumor_id])
    return np.array(gathered_files)


def gather_files_mutect2():
    files = os.listdir('.')
    files.sort()
    gathered_files = []

    for each in files:
        verified_file = False
        normal_id, tumor_id = [False, False]
        f = open(each, 'r', encoding='latin1')
        while not all([verified_file, normal_id, tumor_id]):
            read = f.readline()

            if not read.startswith('#'):
                break

            # Ensure the source is MuTect
            if read.startswith('##GATKCommandLine.MuTect2'):
                verified_file = True
            elif read.startswith('##SAMPLE=<ID=NORMAL,SampleName='):
                normal_id = read.replace('##SAMPLE=<ID=NORMAL,SampleName=', '').split(',')[0]
            elif read.startswith('##SAMPLE=<ID=TUMOR,SampleName='):
                tumor_id = read.replace('##SAMPLE=<ID=TUMOR,SampleName=', '').split(',')[0]

            # BREAK CONDITIONS
            # Don't need to read the entire file if we've found what we need
            if all([normal_id, tumor_id]):
                break
            # This implies a tumor only MuTect2 file which we don't want?
            elif 'tumor_only' in read:
                verified_file = False
                break
        # Do NOT append the file if it is unverified for any reason.
        f.close()
        if verified_file:
            os.rename(each, '{}.vcf'.format(normal_id))
            gathered_files.append(['{}.vcf'.format(normal_id), normal_id, tumor_id, 'NORMAL', 'TUMOR'])
    return np.array(gathered_files)


def gather_files_strelka():
    files = os.listdir('.')
    files.sort()
    gathered_files = []

    for each in files:
        verified_file = False
        flag = False
        tumor_id, normal_id = [False, False]
        f = open(each, 'r')
        while not all([verified_file, flag, normal_id, tumor_id]):
            read = f.readline()

            if not read.startswith('#'):
                break

            # Ensure the source is Strelka
            if read.startswith('##source=strelka'):
                verified_file = True
            elif read.startswith('##content=strelka somatic indel calls'):
                flag = 'indel'
            elif read.startswith('##content=strelka somatic snv calls'):
                flag = 'snv'
            elif read.startswith('##inputs='):
                # Get the patient and sample ID`
                read = read.strip().replace('##inputs=', '').split(' ')
                normal_id, tumor_id = np.array([x.split(':') for x in read])[:, 1]
                # Don't need to read the entire file
                break
        # Do NOT append the file if it is unverified for any reason.
        f.close()
        if verified_file:
            os.rename(each, '{}.{}.vcf'.format(normal_id, flag))
            gathered_files.append([os.path.abspath('{}.{}.vcf'.format(normal_id, flag)),
                                   normal_id,
                                   tumor_id,
                                   'NORMAL',
                                   'TUMOR'])
    return np.array(gathered_files)


def concat_files_strelka(files_and_more):
    body = []
    normal_id = ''
    files_and_more.sort(axis=0)
    # I can do this only because of the renaming that I did previously. This still seems unsafe
    for i in range(len(files_and_more)):
        f = open(files_and_more[i][0], 'r')
        li = f.readlines()
        if ('indel' in files_and_more[i][0].split('.')) and not (normal_id == files_and_more[i][1]):
            normal_id = files_and_more[i][1]
            # Find end of header
            index = max(loc for loc, val in enumerate(li) if '#' in val) + 1
            # Get all text after header
            body = li[index:]
            f.close()
        elif ('snv' in files_and_more[i][0].split('.')) and (normal_id == files_and_more[i][1]):
            # Delete file
            os.remove(files_and_more[i-1][0])
            files_and_more[i-1][0] = '{}.vcf'.format(files_and_more[i-1][1])

            f.close()
            f = open(files_and_more[i][0], 'a')
            f.writelines(body)
            f.close()
            os.rename(files_and_more[i][0], '{}.vcf'.format(normal_id))
            files_and_more[i][0] = '{}.vcf'.format(files_and_more[i][1])
        else:
            # If only an snv or indel file of that name is there
            f.close()
            os.rename(files_and_more[i-1][0], '{}.vcf'.format(normal_id))
            files_and_more[i-1][0] = '{}.vcf'.format(files_and_more[i-1][1])

            # Gather the data from the current file
            f = open(files_and_more[i][0], 'r')
            normal_id = files_and_more[i][1]
            index = max(loc for loc, val in enumerate(li) if '#' in val) + 1
            body = li[index:]
            f.close()
            os.remove(files_and_more[i][0])

    # Remove removed files
    files_and_more = list(files_and_more)
    new_files = os.listdir('.')
    i = len(files_and_more)-1
    while i >= 0:
        try:
            if not os.path.abspath(files_and_more[i][0]) == os.path.abspath(new_files):
                del files_and_more[i-1]
            i -= 1
        except TypeError:
            i -= 1
            pass
    # Remove duplicates
    files_and_more = np.array(list(set(tuple(e) for e in files_and_more)))
    files_and_more.sort(axis=0)
    return files_and_more


def export2maf(files_normals_tumors, args):
    # Load Modules
    if args.force:
        write = True
    else:
        write = False
    # Get all legitimate files
    temp_folder = helper.get_temp_folder(args, 'maf')
    helper.make_folder(temp_folder)
    helper.clean_folder(temp_folder)

    # TODO:: run these in parallel
    for i in range(len(files_normals_tumors)):
        # Figure out if the .maf file should be generated
        vcf = files_normals_tumors[i][0]
        normal_id = files_normals_tumors[i][1]
        tumors_id = files_normals_tumors[i][2]
        gene_col_normal = files_normals_tumors[i][3]
        gene_col_tumors = files_normals_tumors[i][3]
        try:
            os.stat(os.path.basename(vcf) + '.maf')
            if not args.force:
                write = False
        except OSError:
            write = True

        if write:
            subprocess.call('vcf2maf.pl  --input-vcf {} \
                            --output-maf {}/{}.maf       \
                            --normal-id {}              \
                            --tumor-id {}                \
                            --vcf-normal-id {}          \
                            --vcf-tumor-id {}            \
                            --ref-fasta {}              \
                            --filter-vcf {}              \
                            --vep-path $VEP_PATH        \
                            --vep-data $VEP_DATA         \
                            --species homo_sapiens'.format(vcf,
                                                           helper.get_temp_folder(args, 'maf'),
                                                           os.path.splitext(os.path.basename(vcf))[0],
                                                           normal_id,
                                                           tumors_id,
                                                           gene_col_normal,
                                                           gene_col_tumors,
                                                           ref_fasta,
                                                           filter_vcf),
                            shell=True)
        try:
            files_normals_tumors[i][0] = 'maf'.join(files_normals_tumors[i][0].rsplit('vcf'))
            os.remove(vcf)
        except (FileExistsError, OSError):
            pass


def concat_files_maf(files_normals_tumors, args):
    # Yeet all the maf files to the study output folder after concating them
    helper.change_folder(helper.get_temp_folder(args, 'maf'))

    output = open(data_mutations_extended, 'w')
    header = open(files_normals_tumors[0][0])

    output.write(header.readline() + header.readline())
    header.close()

    for files in files_normals_tumors[:, 0]:
        f = open(files, 'r')
        output.writelines(f.readlines()[2:])
        f.close()
    # Now to Yeeeeet it over
    os.rename(os.path.abspath(data_mutations_extended),
              os.path.join(os.path.abspath(args.study_output_folder), data_mutations_extended))
    # Tis been yeeted


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
    f.close()


def main():
    import main_minimal
    args = define_parser().parse_args()
    verb = args.verbose
    main_minimal.gen_mutation_meta_data(args, verb)


if __name__ == '__main__':
    main()
