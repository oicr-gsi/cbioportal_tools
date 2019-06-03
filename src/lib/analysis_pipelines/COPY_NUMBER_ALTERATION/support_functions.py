__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os
import subprocess
import pandas as pd

from lib.support import Config, helper
from lib.constants import constants

## this is for discrete data
thresholds:list  = []


def fix_chrom(exports_config: Config.Config, study_config: Config.Config, verb):
    # Append 'chr' to chromosome if needed
    # Gather ingredients
    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame

    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Removing chr from {}'.format(export_data['FILE_NAME'][i]))
        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(seg_temp, export_data['FILE_NAME'][i])

        output_temp = output_file + '.temp'

        calls.append(helper.parallel_call('awk \'NR>1 {{sub(/\\tchr/,"\\t")}} 1\' {} > {}; '
                                          'mv {} {}'.format(input_file, output_temp, output_temp, output_file), verb))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Segmented format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_seg_id(exports_config: Config.Config, study_config: Config.Config, verb):
    # Replace whatever ID is there with the Sample_ID
    # Gather ingredients
    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame

    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    # Cook
    for i in range(len(export_data)):
        helper.working_on(verb, 'Resolving Sample_ID {}'.format(export_data['FILE_NAME'][i]))

        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(seg_temp, export_data['FILE_NAME'][i])
        sample_id = export_data['SAMPLE_ID'][i]

        output_temp = output_file + '.temp'

        calls.append(helper.parallel_call('head -n 1 "{}" > {}; '.format(input_file, output_temp) +
                                          'cat  {} |'
                                          'awk -F"\\t" \'NR>1 {{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' >> {}; '
                                          'mv {} {}'.format(input_file, sample_id, output_temp,
                                                            output_temp, output_file), verb))
    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Segmented format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_hmmcopy_tsv(exports_config: Config.Config, study_config: Config.Config, verb):
    # Fix the header
    # Gather ingredients
    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    #input(export_data)
    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    bed_filter = subprocess.check_output(['awk "NR>1" {} | '
                                          'awk -F"\\t" \'{{print $1}}\' | '
                                          'uniq'.format(exports_config.config_map['bed_file'])],
                                         shell=True).decode("utf-8")
    #input(bed_filter)
    bed_filter = bed_filter.strip().split('\n')
    bed_filter = bed_filter + ['chr' + a for a in bed_filter]
    bed_filter = ['\\t' + a + '\\t' for a in bed_filter]
    #input(bed_filter)

    header = 'ID\\tchrom\\tloc.start\\tloc.end\\tnum.mark\\tseg.mean'
    # Cook
    for i in range(len(export_data)):
        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(seg_temp, export_data['FILE_NAME'][i])
        sample_id = export_data['SAMPLE_ID'][i]

        helper.working_on(verb, 'Refactoring cols: {}'.format(export_data['FILE_NAME'][i]))
        #input("here")
        output_temp = output_file + '.temp'
        # Get all the genes in the .bed,
        # Save each line with a matching gene
        # Rename the Sample_ID
        #### LEH : this is a difficult to read call to a bash Script
        ###  LEH : it should be rewritten in a python way
        ### replacing the original line with the line below, original maintained.  1 is a placeholder for num.mark columns
        calls.append(helper.parallel_call('echo "{}" > {}; '.format(header, output_temp) +
                                          'cat  {} | '
                                          'awk \'BEGIN{{split("{}",t); for (i in t) vals[t[i]]}} ($2 in vals)\' | '
                                          'awk -F"\\t" \'{{ OFS="\\t"; print "{}", $2, $3, $4, 1, $5}}\' >> '
                                          '{}; '.format(input_file, '|'.join(bed_filter), sample_id, output_temp) +
                                          'mv {} {}'.format(output_temp, output_file),
                                          verb))

        #calls.append(helper.parallel_call('echo "{}" > {}; '.format(header, output_temp) +
        #                                  'cat  {} | '
        #                                  'awk \'BEGIN{{split("{}",t); for (i in t) vals[t[i]]}} ($2 in vals)\' | '
        #                                  'awk -F"\\t" \'{{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' >> '
        #                                  '{}; '.format(input_file, '|'.join(bed_filter), sample_id, output_temp) +
        #                                  'mv {} {}'.format(output_temp, output_file),
        #                                  verb))


    #exit()
    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    #input("here")
    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing HMMCopy format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_hmmcopy_max_chrom(exports_config: Config.Config, study_config: Config.Config, janus_path, verb):
    # Replace chromosome numbers that exceed chromosome length with chromosome length
    # Write num.mark as a n arbitrary operation
    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    # Cook
    for i in range(len(export_data)):

        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(seg_temp, export_data['FILE_NAME'][i])
        dictionary = os.path.join(janus_path, constants.hmmcopy_chrom_positions)

        output_temp = output_file + '.temp'

        calls.append(helper.parallel_call("awk -F'\\t' 'BEGIN {{OFS = FS}} FNR==NR {{dict[$1]=$2; next}} "
                                          "FNR >= 2 {{$4=($4 in dict) ? dict[$4] : $4; $5=int(($4-$3)/1000)}}1' {} {}"
                                          "> {};".format(dictionary, input_file, output_temp) +
                                          'mv {} {}'.format(output_temp, output_file), verb))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing HMMCopy format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def get_sample_ids(exports_config: Config.Config, verb) -> pd.Series:
    data = pd.read_csv(os.path.join(exports_config.config_map['input_folder'],
                                    exports_config.data_frame['FILE_NAME'][0]),
                       sep='\t', usecols=['ID'])

    helper.working_on(verb, message='Parsing importable {} file ...'.format(exports_config.type_config))
    return data['ID'].drop_duplicates(keep='first', inplace=False)


def verify_final_seg_file(exports_config: Config.Config, verb):
    seg = open(os.path.join(exports_config.config_map['input_folder'],
                            exports_config.data_frame['FILE_NAME'][0]), 'w')

    header = seg.readline().strip().split('\t')
    minimum_header = ['ID', 'chrom', 'loc.start', 'loc.end', 'num.mark', 'seg.mean']

    helper.working_on(verb, message='Asserting minimum header is in SEG file.')
    if not all([a in header for a in minimum_header]):
        print([a if a not in header else '' for a in minimum_header])
        print('Missing headers from SEG file have been printed above, please ensure the data is not missing.')
        exit(1)


def gen_log2cna(exports_config: Config.Config, study_config: Config.Config, janus_path, verb):

    # This is log2CNA
    helper.working_on(verb, message='Gathering files ...')
    seg_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map['SEG']))
    bed_file = exports_config.config_map['bed_file']
    l_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config]))

    helper.working_on(verb, message='Generating log2CNA...')

    # This may break if after loading the module R-gsi/3.5.1, Rscript is not set as a constant
    exit_code = helper.call_shell('Rscript {} '
                                  '-s {} '
                                  '-g {} '
                                  '-o {} '.format(os.path.join(janus_path,
                                                               constants.seg2gene), seg_file, bed_file, l_o_file), verb)
    if exit_code == 1:
        helper.stars()
        helper.stars()
        print('R Failed to load libraries, please ensure you\'re using R-gsi/3.5.1')
        exit(1)
    if exit_code == 2:
        helper.stars()
        helper.stars()
        print('There was some error when processing or something. I have no idea')
        exit(2)


def verify_final_continuous_file(exports_config: Config.Config, verb):
    data = open(os.path.join(exports_config.config_map['input_folder'],
                             exports_config.data_frame['FILE_NAME'][0]), 'w')

    t_config = exports_config.type_config
    header = data.readline().strip().split('\t')
    minimum_header = ['Entrez_Gene_Id', 'Hugo_Symbol']

    helper.working_on(verb, message='Asserting minimum header is in {} file.'.format(t_config))
    if not any([a in header for a in minimum_header]):
        print([a if a not in header else '' for a in minimum_header])
        print('Missing header(s) from {} file have been printed above, ensure data isn\'t missing.'.format(t_config))
        exit(1)





def collapse(num):
    [hmzd, htzd, gain, ampl] = thresholds

    if num > ampl:
        return +2

    elif num > gain:
        return +1

    elif num > htzd:
        return +0

    elif num > hmzd:
        return -1

    else:
        return -2


def gen_dcna(exports_config: Config.Config, study_config: Config.Config, verb):

    # This is dCNA
    # Requires cCNA to be generated already
    helper.working_on(verb, message='Gathering files ...')
    l_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map['CONTINUOUS_COPY_NUMBER']))
    c_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config]))
    global thresholds
    thresholds = [float(x) for x in exports_config.config_map['thresholds'].split(',')]
    if os.path.exists(l_o_file):
        helper.working_on(verb, message='Generating dCNA (CNA)...')
        data = pd.read_csv(l_o_file, sep='\t')
        cols = data.columns.values.tolist()[1:]

        # This code here had an astonishing 5500x improvement compared to traversal over it as a 2D array, and yes 5500x
        for c in cols:
            data[c] = data[c].apply(lambda x: collapse(x))

        data.to_csv(c_o_file, sep='\t', index=None)
    else:
        print('ERROR:: Cannot generate dCNA file because log2CNA file does not exist ...')
        print('ERROR:: Either remove the DISCRETE data config file, or add a CONTINUOUS data config file ')
        helper.stars()
        helper.stars()
        exit(1)


def verify_final_discrete_file(exports_config: Config.Config, verb):
    data = open(os.path.join(exports_config.config_map['input_folder'],
                             exports_config.data_frame['FILE_NAME'][0]), 'w')

    t_config = exports_config.type_config
    header = data.readline().strip().split('\t')
    minimum_header = ['Entrez_Gene_Id', 'Hugo_Symbol']

    helper.working_on(verb, message='Asserting minimum header is in {} file.'.format(t_config))
    if not any([a in header for a in minimum_header]):
        print([a if a not in header else '' for a in minimum_header])
        print('Missing header(s) from {} file have been printed above, ensure data isn\'t missing.'.format(t_config))
        exit(1)
