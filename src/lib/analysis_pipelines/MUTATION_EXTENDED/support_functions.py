__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os
import pandas as pd
import numpy as np

from lib.constants.constants import config2name_map
from lib.support import Config, helper

def maf_filter(meta_config, study_config, mutation_type, filter_exception, Minimum_Tumour_Depth = 14, Minimum_Tumour_AF = 0.05, Maximum_gnomAD_AF = 0.001, Maximum_Local_Freq = 0.1):
    # This function replaces the functions below
    # awk -F "\t" 'NR>1' $maf
    # awk -F "\t" '($40>=14)'
    # awk -F "\t" '(($42/$40)>=0.05) && ($133<=0.1) && ( (($124<0.001) && ($17=="unmatched")) || ($17!="unmatched") )'
    # grep -w -f $muttype
    # grep -v -f $filtexc > body
        
    maf_path = os.path.join(study_config.config_map['output_folder'], 'data_{}_concat.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    maf_dataframe = pd.read_csv(maf_path, sep='\t')
    os.remove(maf_path)

    maf_dataframe = maf_dataframe[maf_dataframe['t_depth'] >= float(Minimum_Tumour_Depth)]

    maf_dataframe = maf_dataframe[((maf_dataframe['t_alt_count'] / maf_dataframe['t_depth']) >= float(Minimum_Tumour_AF)) \
            & (maf_dataframe['TGL_Freq'] <= float(Maximum_Local_Freq)) \
            & (((maf_dataframe['gnomAD_AF'] <  float(Maximum_gnomAD_AF)) & (maf_dataframe['Matched_Norm_Sample_Barcode'] == 'unmatched')) | (maf_dataframe['Matched_Norm_Sample_Barcode'] != 'unmatched'))]

    maf_dataframe = maf_dataframe[maf_dataframe.Variant_Classification.isin(mutation_type.split(','))]
    
    filter_list = filter_exception.split(',')
    for j in range(len(filter_list)):
        maf_dataframe = maf_dataframe[~maf_dataframe.FILTER.str.split(';').astype('str').str.contains(filter_list[j])]

    maf_temp = os.path.join(study_config.config_map['output_folder'], 'data_{}_temp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    maf_dataframe.to_csv(maf_temp, sep='\t', index=False)

def oncokb_annotation(meta_config, study_config, oncokb_api_token, verb):
    input_path = os.path.join(study_config.config_map['output_folder'], 'data_{}_temp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    output_path = os.path.join(study_config.config_map['output_folder'], 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    helper.call_shell("MafAnnotator.py -i {} -o {} -b {}".format(input_path, output_path, oncokb_api_token), verb)
    os.remove(input_path)

def TGL_filter(meta_config, study_config):
    data_path = os.path.join(study_config.config_map['output_folder'], 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    maf_dataframe = pd.read_csv(data_path, sep='\t')
    os.remove(data_path)
    
    #Only keep the columns that are given in vep_keep_columns.txt within accessory_files
    vepkeep_file = open(meta_config.config_map['vepkeep'], 'r+')
    vepkeep = [line.rstrip('\n') for line in vepkeep_file.readlines()]
    maf_dataframe = maf_dataframe[vepkeep]

    #Adding columns tumor_vaf and normal_vaf   
    #tumor_vaf column is the result of dividing t_alt_count by t_depth
    maf_dataframe['tumor_vaf'] = maf_dataframe['t_alt_count'].div(maf_dataframe['t_depth'], fill_value = 0)
    maf_dataframe['tumor_vaf'].replace([np.inf, -np.inf], 0)
    #Rearramge tumor_vaf column to be after t_alt_count
    cols = maf_dataframe.columns.tolist()
    cols.insert(maf_dataframe.columns.get_loc('t_alt_count') + 1, cols.pop(cols.index('tumor_vaf')))
    maf_dataframe = maf_dataframe.ix[:, cols]
    print('Inserting tumor_vaf...')

    #tumor_vaf column is the result of dividing n_alt_count by n_depth
    maf_dataframe['normal_vaf'] = maf_dataframe['n_alt_count'].div(maf_dataframe['n_depth'], fill_value = 0)
    maf_dataframe['normal_vaf'].replace([np.inf, -np.inf], 0)
    #Rearramge tumor_vaf_column to be after n_alt_count
    cols = maf_dataframe.columns.tolist()
    cols.insert(maf_dataframe.columns.get_loc('n_alt_count') + 1, cols.pop(cols.index('normal_vaf')))
    maf_dataframe = maf_dataframe.ix[:, cols]
    print('Inserting normal_vaf...')

    #Create oncogenic_binary column based on oncogenic column
    if 'oncogenic' in maf_dataframe.columns:
        maf_dataframe['oncogenic_binary'] = np.where((maf_dataframe['oncogenic'] == 'Oncogenic') | (maf_dataframe['oncogenic'] == 'Likely Oncogenic'), 'YES', 'NO')
        print('Inserting oncogenic_binary...')

    #Create ExAC_common column based on FILTER column
    if 'FILTER' in maf_dataframe.columns:
        maf_dataframe['ExAC_common'] = np.where(maf_dataframe['FILTER'].str.contains('common_variant'), 'YES', 'NO')
        print('Inserting ExAC_common...')

    #Create gnom_AD_AF_POPMAX column using the other gnomAD columns
    maf_dataframe['gnomAD_AF_POPMAX'] = maf_dataframe[['gnomAD_AFR_AF', 'gnomAD_AMR_AF', 'gnomAD_ASJ_AF', 'gnomAD_EAS_AF', 'gnomAD_FIN_AF', "gnomAD_NFE_AF", 'gnomAD_OTH_AF', 'gnomAD_SAS_AF']].max(axis=1)
    print('Inserting gnomAD_AF_POPMAX...')

    #caller artifact filters
    maf_dataframe = maf_dataframe.replace(regex = [r'^clustered_events$', r'^common_variant$', r'^.$'], value = 'PASS')

    # some specific filter flags should be rescued if oncogenic (ie. EGFR had issues here)
    maf_dataframe['FILTER'] = np.where( ( (maf_dataframe['oncogenic_binary'] == 'YES') & ( (maf_dataframe['FILTER'] == 'triallelic_site') | (maf_dataframe['FILTER'] == 'clustered_events;triallelic_site') \
            | (maf_dataframe['FILTER'] == 'clustered_events;homologous_mapping_event') ) ), 'PASS', maf_dataframe['FILTER'])

    # Artifact Filter
    maf_dataframe['TGL_FILTER_ARTIFACT'] = np.where( (maf_dataframe['FILTER'] == 'PASS'), 'PASS', 'Artifact')

    # ExAC Filter
    maf_dataframe['TGL_FILTER_ExAC'] = np.where( ( (maf_dataframe['ExAC_common'] == 'YES') & (maf_dataframe['Matched_Norm_Sample_Barcode'] == 'unmatched') ), 'ExAC_common', 'PASS')

    # gnomAD_AF_POPMAX Filter
    maf_dataframe['TGL_FILTER_gnomAD'] = np.where( ( (maf_dataframe['gnomAD_AF_POPMAX'] > 0.001) & (maf_dataframe['Matched_Norm_Sample_Barcode'] == 'unmatched') ), 'gnomAD_common', 'PASS')

    # VAF Filter
    #maf_dataframe['TGL_FILTER_VAF'] = np.where( ( (maf_dataframe['tumor_vaf'] >= 0.1) | ( (maf_dataframe['tumor_vaf'] < 0.1) & (maf_dataframe['oncogenic_binary'] == 'YES' ) & ) ), )
    maf_dataframe['TGL_FILTER_VAF'] = np.where( ( (maf_dataframe['tumor_vaf'] >= 0.1) | ( (maf_dataframe['tumor_vaf'] < 0.1) & (maf_dataframe['oncogenic_binary'] == 'YES' ) \
            & ( ( (maf_dataframe['Variant_Classification'] == 'In_Frame_Del') | (maf_dataframe['Variant_Classification'] == 'In_Frame_Ins') ) | (maf_dataframe['Variant_Type'] == 'SNP') ) ) ), 'PASS', 'low_VAF')

    # Mark filters
    maf_dataframe['TGL_FILTER_VERDICT'] = np.where( ( (maf_dataframe['TGL_FILTER_ARTIFACT'] == 'PASS') & (maf_dataframe['TGL_FILTER_ExAC'] == 'PASS') & (maf_dataframe['TGL_FILTER_gnomAD'] == 'PASS') \
            & (maf_dataframe['TGL_FILTER_VAF'] == 'PASS') ), 'PASS', (maf_dataframe['TGL_FILTER_ARTIFACT'] + ';' + maf_dataframe['TGL_FILTER_ExAC'] + ';' + maf_dataframe['TGL_FILTER_gnomAD'] + ';' \
            + maf_dataframe['TGL_FILTER_VAF']) )

    # unfiltered data
    os.makedirs(os.path.join(study_config.config_map['output_folder'], 'supplementary_data'), exist_ok=True)
    data_path = os.path.join(study_config.config_map['output_folder'], 'supplementary_data','unfiltered_data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    maf_dataframe.to_csv(data_path, sep='\t', index=False)

    # Filter data if TGL_FILTER_VERDICT has a value of "PASS"
    #maf_dataframe['Matched_Norm_Sample_Barcode'] == 'unmatched'
    maf_dataframe = maf_dataframe[maf_dataframe['TGL_FILTER_VERDICT'] == 'PASS']
            
    data_path = os.path.join(study_config.config_map['output_folder'], 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
    maf_dataframe.to_csv(data_path, sep='\t', index=False)

    # get snvs for dcsigs
    maf_dataframe = maf_dataframe[maf_dataframe['Variant_Type'] == 'SNP']

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
