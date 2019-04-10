__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import subprocess

from lib.support import Config, helper


def wanted_columns(mutate_config: Config.Config, study_config: Config.Config):
    f = open(os.path.join(mutate_config.config_map['input_folder'],
                          mutate_config.data_frame['FILE_NAME'][0]), 'r')
    f.readline()

    wanted = os.path.join(helper.get_temp_folder(study_config.config_map['output_folder'], 'study'),
                          'wanted_columns.txt')

    # Write Columns of Maf File
    helper.make_folder(os.path.dirname(wanted))
    o = open(wanted, 'w+')
    o.write('\n'.join(f.readline().split('\t')))

    f.close()
    o.close()


def filter_vcf_rejects(mutation_config: Config.Config, verb):
    processes = []
    for file in mutation_config.data_frame['FILE_NAME']:
        file = os.path.join(mutation_config.config_map['input_folder'], file)
        processes.append(subprocess.Popen("cat {} | grep -E 'PASS|#' > {}".format(file, file + '.temp'), shell=True))

    # Wait until Baked
    exit_codes = [p.wait() for p in processes]
    if verb:
        print('Exit codes for unfiltered .vcf ...')
        print(exit_codes)
    if any(exit_codes):
        raise ValueError('ERROR:: File not found?')

    processes = []
    for file in mutation_config.data_frame['FILE_NAME']:
        file = os.path.join(mutation_config.config_map['input_folder'], file)
        processes.append(subprocess.Popen("cat {} > {}".format(file + '.temp', file), shell=True))

    # Wait until Baked
    exit_codes = [p.wait() for p in processes]
    if verb:
        print('Exit codes for filtered .vcf ...')
        print(exit_codes)
    if any(exit_codes):
        raise ValueError('ERROR:: Temporary Filter VCF file not found?')


def export2maf(exports_config: Config.Config, study_config: Config.Config, verb):
    # Gather ingredients
    processes = []
    output_folder = study_config.config_map['output_folder']
    export_data = exports_config.data_frame

    maf_temp = helper.get_temp_folder(output_folder, 'maf')

    # Prep
    helper.clean_folder(maf_temp)

    # Cook
    for i in range(export_data.shape[0]):
        # Figure out if the .maf file should be generated
        output_maf = export_data['FILE_NAME'][i]
        output_maf = output_maf.replace('.vcf', '.maf')
        helper.working_on(verb, 'Output .maf being generated... ' + os.path.join(maf_temp, output_maf))

        input_vcf = os.path.join(exports_config.config_map['input_folder'], export_data['FILE_NAME'][i])

        normal_id = export_data['NORMAL_ID'][i]
        tumors_id = export_data['SAMPLE_ID'][i]

        # Since the last 2 columns are optional and represent what's written in the file vs what should be in the output
        if export_data.shape[1] == 6:
            gene_col_normal = export_data['NORMAL_COL'][i]
            gene_col_tumors = export_data['TUMOR_COL'][i]
        elif exports_config.config_map['pipeline'] in ['Mutect']:
            gene_col_normal = normal_id
            gene_col_tumors = tumors_id
        elif exports_config.config_map['pipeline'] in ['Strelka', 'Mutect2']:
            gene_col_normal = 'NORMAL'
            gene_col_tumors = 'TUMOR'
        else:
            gene_col_normal = normal_id
            gene_col_tumors = tumors_id

        ref_fasta = exports_config.config_map['ref_fasta']
        filter_vcf = exports_config.config_map['filter_vcf']

        # Bake in Parallel
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
            exports_config.data_frame['FILE_NAME'][i] = output_maf
        except (FileExistsError, OSError):
            pass
    exports_config.config_map['input_folder'] = maf_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in processes]
    if any(exit_codes):
        raise ValueError('ERROR:: Conversion from vcf 2 maf failed. Please Resolve the issue')
    if verb:
        print(exit_codes)
    return exports_config


def clean_head(exports_config: Config.Config, verb):
    helper.working_on(verb, message='Cleaning head ...')

    processes = []
    for file in exports_config.data_frame['FILE_NAME']:
        file = os.path.join(exports_config.config_map['input_folder'], file)
        processes.append(helper.parallel_call('grep -v \'#\' {0} > {0}.temp;'
                                              'mv {0}.temp {0}'.format(file), verb))

    exit_codes = [p.wait() for p in processes]
    if verb:
        print(exit_codes)
    return exports_config


def zip_maf_files(exports_config: Config.Config, verb) -> Config.Config:
    processes = []
    for i in range(exports_config.data_frame.shape[0]):
        file_name = os.path.join(exports_config.config_map['input_folder'], exports_config.data_frame['FILE_NAME'][i])
        helper.working_on(verb, 'Compressing {} ...'.format(file_name))

        fin = open(file_name, 'r')
        data = fin.read().splitlines(True)
        fout = open(file_name, 'w')
        fout.writelines(data[1:])
        fout.flush()
        fout.close()

        processes.append(subprocess.Popen('gzip {}'.format(file_name),
                                          shell=True))
        exports_config.data_frame['FILE_NAME'][i] += '.gz'

    exit_codes = [p.wait() for p in processes]
    if verb:
        print(exit_codes)
    return exports_config
