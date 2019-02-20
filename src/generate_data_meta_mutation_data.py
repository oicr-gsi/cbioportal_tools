__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import subprocess
import os

import helper
import Config

# Define important constants
ref_fasta = "/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa "
filter_vcf = '/.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz'

data_mutations_extended = 'data_mutations_extended.maf'


def decompress_to_temp(meta_config: Config.Config):
    # Decompresses each file in the current folder to ../temp_vcf/ if it is compressed. otherwise, copy it over
    temp_folder = helper.get_temp_folder(meta_config.config_map['input_folder'], 'vcf')
    helper.make_folder(temp_folder)
    helper.clean_folder(temp_folder)
    for file in os.listdir(temp_folder):
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


def export2maf(exports_config: Config.Config, force, verb):
    # Prep
    temp_folder = helper.get_temp_folder(exports_config.config_map['input_folder'], 'maf')
    helper.make_folder(temp_folder)
    helper.clean_folder(temp_folder)

    # Gather ingredients
    processes = []
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame

    maf_temp = helper.get_temp_folder(input_folder, 'maf')

    # Cook
    for i in range(len(export_data)):
        # Figure out if the .maf file should be generated
        output_maf = 'maf'.join(str(export_data[i][0].replace(i, '') for i in helper.c_choices).rsplit('vcf'))
        input_vcf = os.path.join(helper.get_temp_folder(input_folder, 'vcf'),
                                 'vcf'.join(os.path.basename(output_maf).rsplit('maf')))

        normal_id = export_data[i][2]
        tumors_id = export_data[i][3]

        # Since the last 2 columns are optional
        if export_data.shape[1] == 6:
            gene_col_normal = export_data[i][4]
            gene_col_tumors = export_data[i][5]
        else:
            gene_col_normal = normal_id
            gene_col_tumors = tumors_id

        if os.path.isfile(os.path.basename(output_maf) + '.maf') and not force:
            write = False
        else:
            write = True

        # collect statuses
        if write:
            processes.append(subprocess.Popen('vcf2maf.pl  --input-vcf {}              \
                                                           --output-maf {}/{}           \
                                                           --normal-id {}              \
                                                           --tumor-id {}                \
                                                           --vcf-normal-id {}          \
                                                           --vcf-tumor-id {}            \
                                                           --ref-fasta {}              \
                                                           --filter-vcf {}              \
                                                           --vep-path $VEP_PATH        \
                                                           --vep-data $VEP_DATA         \
                                                           --species homo_sapiens'.format(input_vcf,
                                                                                          maf_temp,
                                                                                          output_maf,
                                                                                          normal_id,
                                                                                          tumors_id,
                                                                                          gene_col_normal,
                                                                                          gene_col_tumors,
                                                                                          ref_fasta,
                                                                                          filter_vcf),
                                              shell=True))

        try:
            exports_config.data_frame[i][0] = output_maf
            exports_config.config_map['input_folder'] = maf_temp
            os.remove(output_maf)
        except (FileExistsError, OSError):
            pass

    # Wait until cooked
    exit_codes = [p.wait() for p in processes]
    if verb:
        print(exit_codes)


def concat_files_maf(meta_config: Config.Config, study_config: Config.Config):
    f_name = helper.get_temp_folder(study_config.config_map['input_folder'], 'maf') + data_mutations_extended
    output = open(f_name, 'w')

    header = open(meta_config.data_frame[0][0])
    output.write(header.readline() + header.readline())
    header.close()

    for files in meta_config.data_frame[:, 0]:
        f = open(files, 'r')
        output.writelines(f.readlines()[2:])
        f.close()

    # Moving concated file
    os.rename(os.path.abspath(f_name),
              os.path.join(os.path.abspath(study_config.config_map['output_folder']), data_mutations_extended))
