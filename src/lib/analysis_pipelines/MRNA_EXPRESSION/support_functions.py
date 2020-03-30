__author__ = ["Kunal Chandan", "Lawrence Heisler"]
__email__ = ["kchandan@uwaterloo.ca", "Lawrence.Heisler@oicr.on.ca"]
__version__ = "1.0"
__status__ = "Production"

import os
import typing
import pandas as pd
import numpy as np
import scipy as sp

from lib.support import Config, helper
from lib.constants.constants import config2name_map
from numpy import *
from scipy.stats import norm

DataFrames = typing.List[pd.DataFrame]

def preProcRNA(meta_config: Config.Config, study_config: Config.Config, enscon, genelist):
    # read in data
    outputPath = study_config.config_map['output_folder']
    gepData = pd.read_csv(outputPath + '/data_expression_continous.txt', sep='\t')
    ensConv = pd.read_csv(enscon, sep='\t')
    ensConv.to_csv(outputPath + '/ensConv.txt', sep='\t', index=False)

    # rename columns
    ensConv.columns = ['gene_id', 'Hugo_Symbol']
    gepData.rename(columns={'Hugo_Symbol':'gene_id'}, inplace=True)

    #ensConv_colnames = ensConv.columns

    #ensConv_colnames[0] = 'gene_id'
    #ensConv_colnames[1] = 'Hugo_Symbol'
    #ensConv.columns = ensConv_colnames

    # merge in Hugo's
    df = pd.merge(gepData, ensConv, on = 'gene_id', how = 'left')
    
    # re-order columns
    newColumns = df.columns.tolist()
    newColumns = newColumns[-1:] + newColumns[1:-1]
    df = df[newColumns]
    ############## TEST 3 ################
    df.to_csv(outputPath + '/test3.txt', sep="\t", index=False)
    ############## TEST 3 ################

    # TODO deduplicate columns
    newColumns = df.columns[0]
    #newColumns = df.columns[1:]
    df = df.drop_duplicates(subset = newColumns)
    
    ############## TEST 2 ################
    df.to_csv(outputPath + '/test2.txt', sep="\t", index=False)
    ############## TEST 2 ################

    # subset with given genelist
    keep_genes_file = open(genelist, 'r+')
    keep_genes = [line.rstrip('\n') for line in keep_genes_file.readlines()]
    keep_genes_file.close()
    df = df[df.Hugo_Symbol.isin(keep_genes)]
    
    df.to_csv(outputPath + '/new_expression.txt', sep="\t", index=False)

    #generating zscores
    raw_scores = df.drop(['Hugo_Symbol'], axis=1)
    means = raw_scores.mean(axis=1)
    sds = raw_scores.std(axis=1)

    z_scores = ((raw_scores.transpose() - means) / sds).transpose()
    z_scores = z_scores.fillna(0)
    z_scores = z_scores.round(decimals=4)
    z_scores_data = pd.concat([df['Hugo_Symbol'], z_scores], axis=1)

    z_scores_data.to_csv(outputPath + '/new_zscores.txt', sep="\t", index=False)

    # Percentile STUDY
    newColumns = z_scores_data.columns
    z_scores_data[newColumns[1:]] = z_scores_data[newColumns[1:]].astype(float)
    newColumns = z_scores_data.columns
    
    # Getting ECD - using scipy
    z_scores_data[newColumns[1:]] = z_scores_data[newColumns[1:]].apply(lambda x: norm.cdf(x))
    z_scores_data[newColumns[1:]] = z_scores_data[newColumns[1:]].round(4)

    # Testing ECDF
    z_scores_data.to_csv(outputPath + '/probability_zscores.txt', sep="\t", index=False)

    # get TCGA comparitor
    tcga_path = meta_config.config_map['tcgadata'] + '/' + meta_config.config_map['tcgacode'] + ".PANCAN.matrix.rdf"
    #df_tcga = pd.read_csv(tcga_path, sep='')
    #print(df_tcga.columns)
    
    # equalize and merge dfs (get common genes)
    #df_stud_tcga = pd.merge(df, df_tcga, how = 'inner', on = )

def get_metadata(meta_config: Config.Config, study_config: Config.Config):
    outputPath = study_config.config_map['output_folder']
    
    meta_expression_path = os.path.join(outputPath, 'new_meta_expression.txt')
    f = open(meta_expression_path, 'w')
    meta_expression = "cancer_study_identifier: " + meta_config.config_map['studyid']
    meta_expression = meta_expression + "\ngenetic_alteration_type: MRNA_EXPRESSION"
    meta_expression = meta_expression + "\ndatatype: CONTINUOUS"
    meta_expression = meta_expression + "\nstable_id: rna_seq_mrna"
    meta_expression = meta_expression + "\nprofile_description: Expression levels RNA-Seq"
    meta_expression = meta_expression + "\nshow_profile_in_analysis_tab: true"
    meta_expression = meta_expression + "\nprofile_name: mRNA expression RNA-Seq"
    meta_expression = meta_expression + "\ndata_filename: data_expression.txt"
    f.writelines(meta_expression)
    f.flush()
    f.close()
    
    meta_zscore_path = os.path.join(outputPath, "new_meta_zscore.txt")
    f = open(meta_zscore_path, 'w')
    meta_zscore = "cancer_study_identifier: " + meta_config.config_map['studyid']
    meta_zscore = meta_zscore + "\ngenetic_alteration_type: MRNA_EXPRESSION"
    meta_zscore = meta_zscore + "\ndatatype: Z-SCORE"
    meta_zscore = meta_zscore + "\nstable_id: rna_seq_mrna_median_Zscores"
    meta_zscore = meta_zscore + "\nshow_profile_in_analysis_tab: true"
    meta_zscore = meta_zscore + "\nprofile_name: mRNA expression z-scores"
    meta_zscore = meta_zscore + "\nprofile_description: Expression levels z-scores"
    meta_zscore = meta_zscore + "\ndata_filename: data_expression_zscores.txt"
    f.writelines(meta_zscore)
    f.flush()
    f.close()

def alpha_sort(exports_config: Config.Config, verb):
    input_folder = exports_config.config_map['input_folder']
    calls = []

    for each in exports_config.data_frame['FILE_NAME']:
        output_file = os.path.join(input_folder, each)

        calls.append(helper.parallel_call('head -n +1 {0} >  {0}.temp;'
                                          'tail -n +2 {0} | sort >> {0}.temp;'
                                          'mv {0}.temp {0}'.format(output_file), verb))

    # Wait until Baked
    exit_codes = [p.wait() for p in calls]

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Cufflinks format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def generate_expression_matrix(exports_config: Config.Config, study_config: Config.Config, verb):
    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.alterationtype + ":" + exports_config.datahandler]))

    helper.working_on(verb, message='Reading FPKM data ...')
    info: DataFrames = []
    for i in range(exports_config.data_frame.shape[0]):
        info.append(pd.read_csv(os.path.join(exports_config.config_map['input_folder'],
                                             exports_config.data_frame['FILE_NAME'][i]),
                                sep='\t',
                                usecols=['gene_id','FPKM'])
                    .rename(columns={'FPKM': exports_config.data_frame['SAMPLE_ID'][i],
                                     'gene_id': 'Hugo_Symbol'})
                    .drop_duplicates(subset='Hugo_Symbol', keep='last', inplace=False))

    helper.working_on(verb, message='Merging all FPKM data ...')
    if len(info) == 0:
        raise ImportError('Attempting to import zero expression data, please remove expression data from study.')
    elif len(info) == 1:
        result = info[0]
    else:
        result = info[0]
        for i in range(1, len(info)):
            result: pd.DataFrame = pd.merge(result, info[i], how='outer', on='Hugo_Symbol')
            result.drop_duplicates(subset='Hugo_Symbol', keep='last', inplace=True)
    result.replace(np.nan, 0, inplace=True)

    helper.working_on(verb, message='Writing all FPKM data ...')
    result.to_csv(output_file, sep='\t', index=None)


def generate_expression_zscore(exports_config: Config.Config, study_config: Config.Config, verb):
    input_file = os.path.join(study_config.config_map['output_folder'],
                              'data_{}.txt'.format(config2name_map[exports_config.alterationtype + ":" + exports_config.datahandler]))

    output_file = os.path.join(study_config.config_map['output_folder'],
                               'data_{}.txt'.format(config2name_map[exports_config.alterationtype + ":Z-SCORE"]))

    # Z-Scores written by Dr. L Heisler
    helper.working_on(verb, message='Reading FPKM Matrix ...')
    raw_data = pd.read_csv(input_file, sep='\t')

    helper.working_on(verb, message='Processing FPKM Matrix ...')
    raw_scores = raw_data.drop(['Hugo_Symbol'], axis=1)
    means = raw_scores.mean(axis=1)
    sds = raw_scores.std(axis=1)

    z_scores = ((raw_scores.transpose() - means) / sds).transpose()
    z_scores = z_scores.fillna(0)
    z_scores = z_scores.round(decimals=4)
    z_scores_data = pd.concat([raw_data['Hugo_Symbol'], z_scores], axis=1)

    helper.working_on(verb, message='Writing FPKM Z-Scores Matrix ...')
    z_scores_data.to_csv(output_file, sep="\t", index=False)
