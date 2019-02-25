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


def decompress_to_temp(mutate_config: Config.Config):
    # Decompresses each file in the current folder to ../temp_vcf/ if it is compressed. otherwise, copy it over
    temp_folder = helper.get_temp_folder(mutate_config.config_map['input_folder'], 'vcf')
    print(temp_folder)
    helper.make_folder(temp_folder)
    helper.clean_folder(temp_folder)
    for file in mutate_config.data_frame.iloc[:, 0]:
        file = os.path.abspath(os.path.join(mutate_config.config_map['input_folder'], file))
        if file.endswith(".tar.gz"):
            subprocess.call("tar -xzf {} -C {}".format(file,
                                                       temp_folder),
                            shell=True)

        elif file.endswith('.gz'):
            subprocess.call("zcat {} > {}/{}".format(file,
                                                     temp_folder,
                                                     os.path.splitext(os.path.basename(file))[0]),
                            shell=True)

        else:
            subprocess.call("cp {} {}".format(file,
                                              temp_folder),
                            shell=True)


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
        output_maf = export_data.iloc[i][0]
        for a in helper.c_choices:
            output_maf = output_maf.replace(a, '')
        output_maf = output_maf.replace('.maf', '.vcf')

        input_vcf = os.path.join(helper.get_temp_folder(input_folder, 'vcf'),
                                 'vcf'.join(os.path.basename(output_maf).rsplit('maf')))

        normal_id = export_data.iloc[i][2]
        tumors_id = export_data.iloc[i][3]

        # Since the last 2 columns are optional and represent what's written in the file vs what should be in the output
        if export_data.shape[1] == 6:
            gene_col_normal = export_data.iloc[i][4]
            gene_col_tumors = export_data.iloc[i][5]
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
            exports_config.data_frame.iloc[i][0] = output_maf
            exports_config.config_map['input_folder'] = maf_temp
            os.remove(output_maf)
        except (FileExistsError, OSError):
            pass
    # Wait until cooked
    exit_codes = [p.wait() for p in processes]
    if verb:
        print(exit_codes)
    return exports_config


def concat_files_maf(mutate_config: Config.Config, study_config: Config.Config):
    print(type(mutate_config))
    f_name = os.path.join(os.path.abspath(study_config.config_map['output_folder']),
                          'data_{}.txt'.format(mutate_config.type_config))
    output = open(f_name, 'w')

    # Write .maf header to output file
    header = open(os.path.join(os.path.abspath(mutate_config.config_map['input_folder']),
                               mutate_config.data_frame.iloc[0][0]))
    output.write(header.readline() + header.readline())
    header.close()

    # Concat the bodies of each of the files to the output
    for files in mutate_config.data_frame.iloc[:, 0]:
        f = open(os.path.join(os.path.abspath(mutate_config.config_map['input_folder']), files), 'r')
        output.writelines(f.readlines()[2:])
        f.close()

    # Ensure file is written to to prevent race condition
    output.flush()
    os.fsync(output)
    output.close()
