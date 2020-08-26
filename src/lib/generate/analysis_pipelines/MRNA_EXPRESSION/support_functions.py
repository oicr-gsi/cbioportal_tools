"""Utility functions for CAP mRNA expression"""

import os
import typing
import pandas as pd
import numpy as np
import scipy as sp
import subprocess

from support import Config, helper
from constants.constants import config2name_map
from numpy import *
from scipy.stats import norm

DataFrames = typing.List[pd.DataFrame]

def preProcRNA(meta_config: Config.Config, study_config: Config.Config, datafile, enscon, genelist, gepcomp, tcga):
    # read in data
    outputPath = study_config.config_map['output_folder']
    try:
        gepData = pd.read_csv(outputPath + datafile, sep='\t')
    except FileNotFoundError:
        print('data_expression_continuous.txt given is a wrong file or wrong file path given from {}'.format(output_Path + datafile))
        raise
    
    try:
        ensConv = pd.read_csv(enscon, sep='\t')
    except FileNotFoundError:
        print('enscon given a wrong file or file path given from {} (enscon is set in the expression config within the headers).'.format(enscon))
        raise
    
    # rename columns
    ensConv.columns = ['gene_id', 'Hugo_Symbol']
    gepData.rename(columns={'Hugo_Symbol':'gene_id'}, inplace=True)

    # merge in Hugo's
    df = pd.merge(gepData, ensConv, on = 'gene_id', how = 'left')

    # re-order columns
    newColumns = df.columns.tolist()
    newColumns = newColumns[-1:] + newColumns[1:-1]
    df = df[newColumns]

    newColumns = df.columns[0]
    df = df.drop_duplicates(subset = newColumns)

    # subset with given genelist
    keep_genes_file = open(genelist, 'r')
    keep_genes = [line.rstrip('\n') for line in keep_genes_file.readlines()]
    keep_genes_file.close()
    df = df[df.Hugo_Symbol.isin(keep_genes)]
   
    # output comparison data
    if gepcomp:
        try:
            df.to_csv(outputPath + '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep="\t", index=False)
        except FileNotFoundError:
            print('{} wrong file or file path'.format(outputPath + '/data_{}_gepcomp.txt'))
            raise

    # output study expression continuous data
    else:
        try:
            df.to_csv(outputPath + '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep="\t", index=False)
        except FileNotFoundError:
            print('{} wrong file or file path'.format(outputPath + '/data_{}.txt'))
            raise

    # output tcga data using the study expression data
    if tcga:
        #equalize samples 
        try:
            tcga_comp = pd.read_csv(meta_config.config_map['tcgadata'], sep='\t')
        except FileNotFoundError:
            print('TCGA file not found from path {}'.format(meta_config.config_map['tcgadata']))
            raise

        # TODO TODO TODO TODO TODO TODO TEST IF YOU CAN RUN WITHOUT THIS LINE - MAY BE REDUNDANT CODE
        #df = pd.read_csv(outputPath + '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep='\t')

        intersected_Hugo_Symbols = set(tcga_comp['Hugo_Symbol']).intersection(df['Hugo_Symbol'].tolist())

        df_tcga_common = tcga_comp[tcga_comp.Hugo_Symbol.isin(intersected_Hugo_Symbols)]
        df_stud_common = df[df.Hugo_Symbol.isin(intersected_Hugo_Symbols)]

        # Reindex TCGA dataframe
        df_tcga_common.reindex(df_stud_common['Hugo_Symbol'].tolist())

        # merge samples
        df_stud_tcga = pd.merge(df_stud_common, df_tcga_common, on = 'Hugo_Symbol', how = 'inner')
        
        # output merged samples
        try:
            df_stud_tcga.to_csv(outputPath + '/data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep="\t", index=False)
        except FileNotFoundError:
            print('{} wrong file or file path'.format(outputPath + '/data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler])))
            raise

def alpha_sort(exports_config: Config.Config, verb):
    input_folder = exports_config.config_map['input_folder']
    calls = []
    for each in exports_config.data_frame['FILE_NAME']:
        output_file = os.path.join(input_folder, each)
        cmd = 'head -n +1 '+\
              '{0} > {0}.temp; tail -n +2 {0} | sort >> {0}.temp; mv {0}.temp {0}'.format(output_file)
        calls.append(subprocess.Popen(cmd, shell=True))
    exit_codes = [p.wait() for p in calls]

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Cufflinks format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def generate_expression_matrix(exports_config: Config.Config, study_config: Config.Config, verb):
    # Output for data_expression_continuous_expression.txt data file
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

    # Append the gepcomp datafiles (if any)
    gep_file = exports_config.config_map.get('gepfile')
    if gep_file != None and os.path.exists(gep_file):
        geplist = pd.read_csv(gep_file, sep=',')
        geplist.columns = ['patient_id', 'file_name']
 
        # Filter out the patient ID's that have already been included in the study
        indices = []
        for i in range(exports_config.data_frame.shape[0]):
            for a, elem in enumerate(geplist.patient_id.tolist()):
                if exports_config.data_frame['PATIENT_ID'][i] in elem:
                    indices.append(a)
        geplist = geplist.drop(indices)

        for index, row in geplist.iterrows():
            info.append(pd.read_csv(row.file_name,
                                sep='\t',
                                usecols=['gene_id','FPKM'])
            .rename(columns={'FPKM': row.patient_id,
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
                result: pd.DataFrame = pd.merge(result, info[i], how='left', on='Hugo_Symbol')
                result.drop_duplicates(subset='Hugo_Symbol', keep='last', inplace=True)
        result.replace(np.nan, 0, inplace=True)

        helper.working_on(verb, message='Writing all FPKM data ...')
    
        # Output the gepcomp data
        output_file_comp = os.path.join(study_config.config_map['output_folder'], 
                'data_{}_gepcomp.txt'.format(config2name_map[exports_config.alterationtype + ":" + exports_config.datahandler]))
        result.to_csv(output_file_comp, sep='\t', index=None)

def generate_expression_zscore(meta_config: Config.Config, input_file, outputPath, gepcomp, tcga, verb):
    # Z-Scores written by Dr. L Heisler
    helper.working_on(verb, message='Reading FPKM Matrix ...')
    try:
        raw_data = pd.read_csv(input_file, sep='\t')
    except FileNotFoundError:
        print('{} wrong file or file path'.format(input_file))
        raise

    helper.working_on(verb, message='Processing FPKM Matrix ...')
    raw_scores = raw_data.drop(['Hugo_Symbol'], axis=1)
    means = raw_scores.mean(axis=1)
    sds = raw_scores.std(axis=1)

    z_scores = ((raw_scores.transpose() - means) / sds).transpose()
    z_scores = z_scores.fillna(0)
    z_scores_data = z_scores.round(decimals=4)
    z_scores_data = pd.concat([raw_data['Hugo_Symbol'], z_scores_data], axis=1)

    helper.working_on(verb, message='Writing FPKM Z-Scores Matrix ...')

    # Reformat the columns for comparison and TCGA data to keep only the columns used in the study mRNA expression continuous data
    if gepcomp or tcga:
        study_columns = []
        for k in range(meta_config.data_frame.shape[0]):
            study_columns.append(meta_config.data_frame['SAMPLE_ID'][k])
        study_columns.insert(0,'Hugo_Symbol')
        z_scores_data = z_scores_data[study_columns]
        
        # Create the supplementary_data directory if it doesn't exist
        if not os.path.exists(os.path.join(outputPath, 'supplementary_data')):
            os.makedirs(os.path.join(outputPath, 'supplementary_data'), exist_ok=True)
    
    if gepcomp:
        # Output comparison Z scores
        output_file_z_scores = os.path.join(outputPath, 'supplementary_data', 'data_{}_comparison.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE']))
        z_scores_data.to_csv(output_file_z_scores, sep="\t", index=False)

        # Delete all gepcomp files that are not in the supplementary folder
        os.remove(input_file)

    elif tcga:
        # Output TCGA Z scores
        output_file_z_scores = os.path.join(outputPath, 'supplementary_data', 'data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE']))
        z_scores_data.to_csv(output_file_z_scores, sep="\t", index=False)
        
        # Delete all TCGA files that are not in the supplementary folder
        os.remove(input_file)
        
    else:
        # Output study Z scores
        output_file_z_scores = os.path.join(outputPath, 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'Z-SCORE']))
        z_scores_data.to_csv(output_file_z_scores, sep="\t", index=False)

# Input for this function should be a mRNA expression z-score file
def generate_expression_percentile(meta_config: Config.Config, input_file, outputPath, gepcomp, tcga, verb):
    # Load in z-score file
    try:
        z_scores_data = pd.read_csv(input_file, sep='\t')
    except FileNotFoundError:
        print('{} wrong file or file path'.format(input_file))
        raise

    # Percentile STUDY
    newColumns = z_scores_data.columns
    percentile_data = z_scores_data[newColumns[1:]].astype(float)

    # Getting ECD - using scipy
    percentile_data = percentile_data.apply(lambda x: norm.cdf(x))
    percentile_data = percentile_data.round(4)
    percentile_data = pd.concat([z_scores_data['Hugo_Symbol'], percentile_data], axis=1)

    # Handle for mRNA expression continuous percentile comparison data
    if gepcomp:
        study_columns = []
        for k in range(meta_config.data_frame.shape[0]):
            study_columns.append(meta_config.data_frame['SAMPLE_ID'][k])
        study_columns.insert(0,'Hugo_Symbol')
        percentile_data = percentile_data[study_columns]

        # Create directory if it doesn't exist
        if not os.path.exists(os.path.join(outputPath, 'supplementary_data')):
            os.makedirs(os.path.join(outputPath, 'supplementary_data'), exist_ok=True)

        # Output comparison ECDF
        output_file_percentile = os.path.join(outputPath, 'supplementary_data', 'data_{}_comparison.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'PERCENTILE']))
        percentile_data.to_csv(output_file_percentile, sep="\t", index=False)
   
    # Handle for TCGA percentile data
    elif tcga:
        # Create directory if it doesn't exist
        if not os.path.exists(os.path.join(outputPath, 'supplementary_data')):
            os.makedirs(os.path.join(outputPath, 'supplementary_data'), exist_ok=True)
        # Output comparison ECDF
        output_file_percentile = os.path.join(outputPath, 'supplementary_data', 'data_{}_tcga.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'PERCENTILE']))
        percentile_data.to_csv(output_file_percentile, sep="\t", index=False)


    # Handle for mRNA expression continuous percentile data
    else:
        # Create directory if it doesn't exist
        if not os.path.exists(os.path.join(outputPath, 'supplementary_data')):
            os.makedirs(os.path.join(outputPath, 'supplementary_data'), exist_ok=True)
        # Output comparison ECDF
        output_file_percentile = os.path.join(outputPath, 'supplementary_data', 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + 'PERCENTILE']))
        percentile_data.to_csv(output_file_percentile, sep="\t", index=False)
