__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import subprocess
import multiprocessing

import pandas as pd

from lib.support import Config, helper
from lib import constants

# Define important constants
segmented_pipelines = ['CNVkit', 'Sequenza', 'HMMCopy.tsv', 'HMMCopy.seg']

max_process = 5


def remove_chr(seg_file: str, input_location: str, output_location: str, verb):
    input_file = os.path.join(input_location, seg_file)
    output_file = os.path.join(output_location, seg_file)

    if input_file == output_file:
        output_temp = output_file + '.temp'

        helper.call_shell('awk \'NR>1 {{sub(/\\tchr/,"\\t")}} 1\' {} > {}'.format(input_file, output_temp), verb)
        helper.call_shell('mv {} {}'.format(output_temp, output_file), verb)
    else:

        helper.call_shell('awk \'NR>1 {{sub(/\\tchr/,"\\t")}} 1\' {} > {}'.format(input_file, output_file), verb)


def set_id(seg_file: str, input_location: str, output_location: str, sample_id: str, verb):

    input_file = os.path.join(input_location, seg_file)
    output_file = os.path.join(output_location, seg_file)

    if input_file == output_file:
        output_temp = output_file + '.temp'

        helper.call_shell('head -1 "{}" > {}'.format(input_file, output_temp), verb)
        helper.call_shell('cat  {} |'
                          'awk -F"\\t" \'NR>1 {{ OFS="\\t"; print {}, $2, $3, $4, $5, $6}}\' '
                          '>> {}'.format(input_file, sample_id, output_temp), verb)
        helper.call_shell('mv {} {}'.format(output_temp, output_file), verb)
    else:

        helper.call_shell('head -1 "{}" > {}'.format(input_file, output_file), verb)
        helper.call_shell('cat  {} |'
                          'awk -F"\\t" \'NR>1 {{ OFS="\\t"; print {}, $2, $3, $4, $5, $6}}\' '
                          '>> {}'.format(input_file, sample_id, output_file), verb)


def hmmcopy_seg_2_standard(seg_file: str, input_location: str, output_location: str, bed_filter: list, verb):

    input_file = os.path.join(input_location, seg_file)
    output_file = os.path.join(output_location, seg_file)

    header = 'ID\\tchrom\\tloc.start\\tloc.end\\tnum.mark\\tseg.mean'

    if input_file == output_file:
        output_temp = output_file + '.temp'

        helper.call_shell('echo "{}" > {}'.format(header, output_temp), verb)
        helper.call_shell('cat  {} | '
                          'grep -P "{}" | '
                          'awk "NR>1" | '
                          'awk -F"\\t" \'{{ OFS="\\t"; print $1, $2, $3, $4, ($4-$3), $5}}\' '
                          '>> {}'.format(input_file, '|'.join(bed_filter), output_temp), verb)
        helper.call_shell('mv {} {}'.format(output_temp, output_file), verb)

    else:

        helper.call_shell('echo "{}" > {}'.format(header, output_file), verb)
        helper.call_shell('cat  {} | '
                          'grep -P "{}" | '
                          'awk "NR>1"| '
                          'awk -F"\\t" \'{{ OFS="\\t"; print $1, $2, $3, $4, ($4-$3), $5}}\' >> '
                          '{}'.format(input_file, '|'.join(bed_filter), output_file), verb)


def hmmcopy_tsv_2_standard(tsv_file: str, input_location: str, output_location: str, bed_filter: list, sample_id: str, verb):

    input_file = os.path.join(input_location, tsv_file)
    output_file = os.path.join(output_location, tsv_file)

    header = 'ID\\tchrom\\tloc.start\\tloc.end\\tnum.mark\\tseg.mean'
    print(bed_filter)
    if input_file == output_file:
        output_temp = output_file + '.temp'

        helper.call_shell('echo "{}" > {}'.format(header, output_temp), verb)
        helper.call_shell('cat  {} | '
                          'awk \'BEGIN{{split("{}",t); for (i in t) vals[t[i]]}} ($2 in vals)\' | '
                          'awk -F"\\t" \'{{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' >> '
                          '{}'.format(input_file, '|'.join(bed_filter), sample_id, output_temp), verb)
        helper.call_shell('mv {} {}'.format(output_temp, output_file), verb)
    else:
        helper.call_shell('echo "{}" > {}'.format(header, output_file), verb)
        helper.call_shell('cat  {} | '
                          'awk \'BEGIN{{split("{}",t); for (i in t) vals[t[i]]}} ($2 in vals)\' | '
                          'awk -F"\\t" \'{{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' >> '
                          '{}'.format(input_file, ' '.join(bed_filter), sample_id, output_file), verb)


def fix_chrom(exports_config: Config.Config, study_config: Config.Config, verb):
    # Gather ingredients
    pool = multiprocessing.Pool(processes=max_process)
    processes = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame

    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Removing chr from {}'.format(export_data['FILE_NAME'][i]))
        processes.append(pool.apply_async(remove_chr, [export_data['FILE_NAME'][i], input_folder, seg_temp, verb]))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.get() for p in processes]

    # Clean up
    pool.close()
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Sequenza format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_seg_id(exports_config: Config.Config, study_config: Config.Config, verb):

    # Gather ingredients
    pool = multiprocessing.Pool(processes=max_process)
    processes = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame

    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Removing chr from {}'.format(export_data['FILE_NAME'][i]))
        processes.append(pool.apply_async(set_id, [export_data['FILE_NAME'][i],
                                                   input_folder,
                                                   seg_temp,
                                                   export_data['TUMOR_ID'][i],
                                                   verb]
                                          ))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.get() for p in processes]

    # Clean up
    pool.close()
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Sequenza format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_hmmcopy_seg(exports_config: Config.Config, study_config: Config.Config, verb):

    # Gather ingredients
    pool = multiprocessing.Pool(processes=max_process)
    processes = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    bed_filter = subprocess.check_output(['awk "NR>1" {} | awk -F"\\t" \'{{print $1}}\' | uniq'.format(constants.bed_file)], shell=True).decode("utf-8")
    bed_filter = bed_filter.strip().split('\n')
    bed_filter = bed_filter + ['chr' + a for a in bed_filter]
    bed_filter = ['\\t' + a + '\\t' for a in bed_filter]
    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Refactoring cols: {}'.format(export_data['FILE_NAME'][i]))
        processes.append(pool.apply_async(hmmcopy_seg_2_standard, [export_data['FILE_NAME'][i],
                                                                   input_folder,
                                                                   seg_temp,
                                                                   bed_filter,
                                                                   verb]))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.get() for p in processes]

    # Clean up
    pool.close()
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Sequenza format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_hmmcopy_tsv(exports_config: Config.Config, study_config: Config.Config, verb):

    # Gather ingredients
    pool = multiprocessing.Pool(processes=max_process)
    processes = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    bed_filter = subprocess.check_output(['awk "NR>1" {} | awk -F"\\t" \'{{print $1}}\' | uniq'.format(constants.bed_file)], shell=True).decode("utf-8")
    bed_filter = bed_filter.strip().split('\n')
    bed_filter = bed_filter + ['chr' + a for a in bed_filter]
    bed_filter = ['\\t' + a + '\\t' for a in bed_filter]

    print(export_data['TUMOR_ID'][0])
    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Refactoring cols: {}'.format(export_data['FILE_NAME'][i]))
        processes.append(pool.apply_async(hmmcopy_tsv_2_standard, [export_data['FILE_NAME'][i],
                                                                   input_folder,
                                                                   seg_temp,
                                                                   bed_filter,
                                                                   export_data['TUMOR_ID'][i],
                                                                   verb]))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.get() for p in processes]

    # Clean up
    pool.close()
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Sequenza format file? Please resolve the issue')
    if verb:
        print(exit_codes)