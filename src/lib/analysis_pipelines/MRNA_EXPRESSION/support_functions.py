__author__ = ["Kunal Chandan", "Lawrence Heisler"]
__email__ = ["kchandan@uwaterloo.ca", "Lawrence.Heisler@oicr.on.ca"]
__version__ = "1.0"
__status__ = "Production"

import os
import typing
import pandas as pd
import numpy as np
import scipy as sp
import subprocess

from lib.support import Config, helper
from lib.constants.constants import config2name_map
from numpy import *
from scipy.stats import norm

DataFrames = typing.List[pd.DataFrame]

def preProcRNA(meta_config: Config.Config, study_config: Config.Config, datafile, enscon, genelist, gepcomp):
    # read in data
    outputPath = study_config.config_map['output_folder']
    gepData = pd.read_csv(outputPath + datafile, sep='\t')
    ensConv = pd.read_csv(enscon, sep='\t')

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
    keep_genes_file = open(genelist, 'r+')
    keep_genes = [line.rstrip('\n') for line in keep_genes_file.readlines()]
    keep_genes_file.close()
    df = df[df.Hugo_Symbol.isin(keep_genes)]
   
    if gepcomp:
        df.to_csv(outputPath + '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep="\t", index=False)

    else:
        df.to_csv(outputPath + '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep="\t", index=False)

def generate_TCGA_data(meta_config: Config.Config, study_config: Config.Config):
    outputPath = study_config.config_map['output_folder']

    ## get TCGA comparitor
    #tcga_path = meta_config.config_map['tcgadata'] + '/' + meta_config.config_map['tcgacode'] + ".PANCAN.matrix.rdf"
    
    ## R alternative
    #command = '/.mounts/labs/gsi/modulator/sw/Ubuntu18.04/rstats-3.6/bin/Rscript'
    #path2script = '/.mounts/labs/gsiprojects/gsi/cBioGSI/aliang/cbioportal_tools/src/lib/analysis_pipelines/MRNA_EXPRESSION/get_tcga.r'
    #args = [tcga_path, meta_config.config_map['tcgacode'], outputPath]
    #cmd = [command, path2script] + args

    #subprocess.call(cmd)

    #equalize samples 
    tcga_comp = pd.read_csv(meta_config.config_map['tcgadata'], sep='\t')
    df = pd.read_csv(outputPath + '/data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]), sep='\t')
     
    intersected_Hugo_Symbols = set(tcga_comp['Hugo_Symbol']).intersection(df['Hugo_Symbol'].tolist())

    df_tcga_common = tcga_comp[tcga_comp.Hugo_Symbol.isin(intersected_Hugo_Symbols)]
    df_stud_common = df[df.Hugo_Symbol.isin(intersected_Hugo_Symbols)]
    
    # Reindex TCGA dataframe
    df_tcga_common.reindex(df_stud_common['Hugo_Symbol'].tolist())

    # merge samples
    df_stud_tcga = pd.merge(df_stud_common, df_tcga_common, on = 'Hugo_Symbol', how = 'inner')
    
    df_temp = df_stud_tcga[df_stud_common.columns.tolist()]
     
    #generating zscores
    raw_scores = df_stud_tcga.drop(['Hugo_Symbol'], axis=1)
    means = raw_scores.mean(axis=1)
    sds = raw_scores.std(axis=1)

    z_scores = ((raw_scores.transpose() - means) / sds).transpose()
    z_scores = z_scores.fillna(0)
    z_scores_data = z_scores.round(decimals=4)
    z_scores_data = pd.concat([df_stud_tcga['Hugo_Symbol'], z_scores_data], axis=1)
    
    z_scores_data = z_scores_data[df_stud_common.columns.tolist()]
    z_scores_data.to_csv(os.path.join(outputPath, 'supplementary_data', 'data_expression_zscores_tcga.txt'), sep="\t", index=False)

    # Percentile STUDY
    newColumns = z_scores_data.columns
    z_scores_data[newColumns[1:]] = z_scores_data[newColumns[1:]].astype(float)
    newColumns = z_scores_data.columns

    # Getting ECD - using scipy
    z_scores_data[newColumns[1:]] = z_scores_data[newColumns[1:]].apply(lambda x: norm.cdf(x))
    z_scores_data[newColumns[1:]] = z_scores_data[newColumns[1:]].round(4)
    
    # Generate TCGA percentile data
    z_scores_data.to_csv(os.path.join(outputPath, 'supplementary_data', 'data_expression_percentile_tcga.txt'), sep="\t", index=False)


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

    #Append the gepcomp datafiles
    if os.path.exists(exports_config.config_map['gepfile']):
        geplist = pd.read_csv(exports_config.config_map['gepfile'], sep=',')
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

def generate_expression_zscore(meta_config: Config.Config, input_file, outputPath, gepcomp, verb):
    zscoreFile = 'data_{}.txt'.format(config2name_map[meta_config.alterationtype + ":Z-SCORE"])
    percentileFile = 'data_expression_percentile.txt'

    # Z-Scores written by Dr. L Heisler
    helper.working_on(verb, message='Reading FPKM Matrix ...')
    raw_data = pd.read_csv(input_file, sep='\t')

    helper.working_on(verb, message='Processing FPKM Matrix ...')
    raw_scores = raw_data.drop(['Hugo_Symbol'], axis=1)
    means = raw_scores.mean(axis=1)
    sds = raw_scores.std(axis=1)

    z_scores = ((raw_scores.transpose() - means) / sds).transpose()
    z_scores = z_scores.fillna(0)
    z_scores_data = z_scores.round(decimals=4)
    z_scores_data = pd.concat([raw_data['Hugo_Symbol'], z_scores_data], axis=1)

    helper.working_on(verb, message='Writing FPKM Z-Scores Matrix ...')
    
    # Percentile STUDY
    newColumns = z_scores_data.columns
    percentile_data = z_scores_data[newColumns[1:]].astype(float)
    newColumns = percentile_data.columns

    # Getting ECD - using scipy
    percentile_data = percentile_data.apply(lambda x: norm.cdf(x))
    percentile_data = percentile_data.round(4)
    percentile_data = pd.concat([raw_data['Hugo_Symbol'], percentile_data], axis=1)

    if gepcomp:
        study_columns = []
        for k in range(meta_config.data_frame.shape[0]):
            study_columns.append(meta_config.data_frame['SAMPLE_ID'][k])
        study_columns.insert(0,'Hugo_Symbol')
        z_scores_data = z_scores_data[study_columns]
        percentile_data = percentile_data[study_columns]
        zscoreFile = 'data_expression_zscores_comparison.txt'
        percentileFile = 'data_expression_percentile_comparison.txt'
        
        # Create directory if it doesn't exist
        if not os.path.exists(os.path.join(outputPath, 'supplementary_data')):
            os.makedirs(os.path.join(outputPath, 'supplementary_data'), exist_ok=True)
        
        # Output comparison Z scores
        z_scores_data.to_csv(os.path.join(outputPath, 'supplementary_data', zscoreFile), sep="\t", index=False)

        # Output comparison ECDF
        percentile_data.to_csv(os.path.join(outputPath, 'supplementary_data', percentileFile), sep="\t", index=False)

        # Delete all gepcomp files that are not in the supplementary folder
        os.remove(outputPath + '/data_{}_gepcomp.txt'.format(config2name_map[meta_config.alterationtype + ":" + meta_config.datahandler]))
        
    else:
        # Output study Z scores
        z_scores_data.to_csv(outputPath + zscoreFile, sep="\t", index=False)

        # Create directory if it doesn't exist
        if not os.path.exists(os.path.join(outputPath, 'supplementary_data')):
            os.makedirs(os.path.join(outputPath, 'supplementary_data'), exist_ok=True)
        
        # Output study ECDF
        percentile_data.to_csv(os.path.join(outputPath, 'supplementary_data', percentileFile), sep="\t", index=False)
