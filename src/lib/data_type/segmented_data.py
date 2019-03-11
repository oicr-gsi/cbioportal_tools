__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import multiprocessing

import pandas as pd

from lib.support import Config, helper

# Define important constants
segmented_pipelines = ['CNVkit', 'FREEC']


def remove_chr(seg_file: str, input_location: str, output_location: str):
    input_file = os.path.join(input_location, seg_file)
    output_file = os.path.join(output_location, seg_file)

    if os.path.isfile(input_file):
        tsv = pd.read_csv(input_file, sep='\t')

        chrom = tsv['chrom']
        chrom = chrom.apply(lambda x: x.strip('chr'))
        tsv['chrom'] = chrom

        tsv.to_csv(output_file, sep='\t', index=None)
    else:
        raise IOError('ERROR:: Something went wrong and you\'re missing some Segmented files.')


def fix_sequenza_chrom(exports_config: Config.Config, study_config: Config.Config, verb):
    # Gather ingredients
    pool = multiprocessing.Pool()
    processes = []
    output_folder = study_config.config_map['output_folder']
    export_data = exports_config.data_frame

    seg_temp = helper.get_temp_folder(output_folder, 'seg')
    input_folder = exports_config.config_map['input_folder']

    remove_chr(export_data['FILE_NAME'][0], input_folder, seg_temp)
    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Removing chr from {}'.format(export_data['FILE_NAME'][i]))
        processes.append(pool.apply_async(remove_chr, [export_data['FILE_NAME'][i], input_folder, seg_temp]))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.get() for p in processes]
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Sequenza format file? Please Resolve the issue')
    if verb:
        print(exit_codes)
    return exports_config
