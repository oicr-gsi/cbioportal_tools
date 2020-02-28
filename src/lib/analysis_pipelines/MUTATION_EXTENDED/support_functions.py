__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os
import pandas as pd

from lib.support import Config, helper

def maf_filter(maf, t_depth, t_alt_count, TGL_Freq, gnomAD_AF, mutation_type, filter_exception, output_folder):
    #(($42/$40)>=0.05) && ($133<=0.1) && ( (($124<0.001) && ($17=="unmatched")) || ($17!="unmatched") )
    maf_dataframe = pd.read_csv(maf, sep='\t')
    maf_dataframe = maf_dataframe[maf_dataframe.t_depth.isin(t_depth) & ]

def verify_dual_columns(exports_config: Config.Config, verb):
    processes = []
    for i in range(exports_config.data_frame.shape[0]):
        file = os.path.join(exports_config.config_map['input_folder'], exports_config.data_frame['FILE_NAME'][i])
        # if the normal_id is UNMATCHED, then do this silly business.
        if exports_config.data_frame['NORMAL_ID'][i] == 'UNMATCHED':

            # Essentially, print the header,
            # add an unmatched column to header,
            # duplicate last column
            processes.append(helper.parallel_call('awk -F\'\\t\' \'{{ OFS = FS }} '
                                                  '{{   if ($1 ~ "##"){{ print }} '
                                                  'else if ($1 ~ "#"){{ for(i = 1; i <= NF;i++){{ printf "%s\\t", $i }}'
                                                  ' print "UNMATCHED" }}'
                                                  'else {{ for(i = 1; i <= NF; i++){{ printf "%s\\t", $i}} print $NF }}'
                                                  '}}\' {0} > {0}.temp;'
                                                  'mv {0}.temp {0}'.format(file), verb))
    # Wait until Baked
    exit_codes = [p.wait() for p in processes]
    if verb:
        print('Exit codes for filtered .vcf ...')
        print(exit_codes)
    if any(exit_codes):
        raise ValueError('ERROR:: VCF file not found? or AWK Failed?')


def filter_vcf_rejects(mutation_config: Config.Config, verb):
    # Filter for only PASS
    processes = []
    for file in mutation_config.data_frame['FILE_NAME']:
        file = os.path.join(mutation_config.config_map['input_folder'], file)
        processes.append(helper.parallel_call("cat {} | grep -E 'PASS|#' > {}".format(file, file + '.temp'), verb))

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
        processes.append(helper.parallel_call("cat {} > {}".format(file + '.temp', file), verb))

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

    # Prep  ### LEH : not clear why this temp folder was being cleared output
    #helper.clean_folder(maf_temp,True)

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

        # ORIGINAL -- 
        ref_fasta = exports_config.config_map['ref_fasta']
        # TESTING --
        #ref_fasta = exports_config.config_map['$HG19_ROOT/hg19_random.fa']
        filter_vcf = exports_config.config_map['filter_vcf']

        # Bake in Parallel
        processes.append(helper.parallel_call('vcf2maf  --input-vcf {}    '
                                                       '--output-maf {}/{}   '
                                                       '--normal-id {}       '
                                                       '--tumor-id {}        '
                                                       '--vcf-normal-id {}   '
                                                       '--vcf-tumor-id {}    '
                                                       '--ref-fasta {}       '
                                                       '--filter-vcf {}      '
                                                       '--vep-path $VEP_PATH '
                                                       '--vep-data $VEP_DATA '
                                                       '--species homo_sapiens'.format(input_vcf,
                                                                                      maf_temp,
                                                                                      output_maf,
                                                                                      normal_id,
                                                                                      tumors_id,
                                                                                      gene_col_normal,
                                                                                      gene_col_tumors,
                                                                                      ref_fasta,
                                                                                      filter_vcf),
                                              verb))
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
    # Remove excess header from top of MAF files
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


def get_sample_ids(exports_config: Config.Config, verb) -> pd.Series:
    data = pd.read_csv(os.path.join(exports_config.config_map['input_folder'],
                                    exports_config.data_frame['FILE_NAME'][0]),
                       sep='\t', skiprows=1, usecols=['Tumor_Sample_Barcode'])
    # Skip header #version2.4
    helper.working_on(verb, message='Parsing importable {} file ...'.format(exports_config.type_config))
    return data['Tumor_Sample_Barcode'].drop_duplicates(keep='first', inplace=False)


def verify_final_file(exports_config: Config.Config, verb):
    maf = open(os.path.join(exports_config.config_map['input_folder'],
                            exports_config.data_frame['FILE_NAME'][0]), 'w')

    header = maf.readline().strip().split('\t')
    minimum_header = ['Hugo_Symbol', 'Tumor_Sample_Barcode', 'Variant_Classification', 'HGVSp_Short']

    helper.working_on(verb, message='Asserting minimum header is in MAF file.')
    if not all([a in header for a in minimum_header]):
        print([a if a not in header else '' for a in minimum_header])
        print('Missing headers from MAF file have been printed above, please ensure the data is not missing.')
        exit(1)
