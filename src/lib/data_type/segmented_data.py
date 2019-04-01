__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import subprocess

from lib.support import Config, helper
from lib.constants import constants

# Define important constants
segmented_pipelines = ['CNVkit', 'Sequenza', 'HMMCopy']


def fix_chrom(exports_config: Config.Config, study_config: Config.Config, verb):
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

        if input_file == output_file:
            output_temp = output_file + '.temp'

            calls.append(helper.parallel_call('awk \'NR>1 {{sub(/\\tchr/,"\\t")}} 1\' {} > {}; '.format(input_file,
                                                                                                        output_temp) +
                                              'mv {} {}'.format(output_temp, output_file),
                                              verb))
        else:

            calls.append(helper.parallel_call('awk \'NR>1 {{sub(/\\tchr/,"\\t")}} 1\' {} > {}'.format(input_file,
                                                                                                      output_file),
                                              verb))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Segmented format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_seg_id(exports_config: Config.Config, study_config: Config.Config, verb):

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
        sample_id = export_data['TUMOR_ID'][i]

        if input_file == output_file:
            output_temp = output_file + '.temp'

            calls.append(helper.parallel_call('head -n 1 "{}" > {}; '.format(input_file, output_temp) +
                                              'cat  {} |'
                                              'awk -F"\\t" \'NR>1 {{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' '
                                              '>> {}; '.format(input_file, sample_id, output_temp) +
                                              'mv {} {}'.format(output_temp, output_file), verb))
        else:

            calls.append(helper.parallel_call('head -n 1 "{}" > {}; '.format(input_file, output_file) +
                                              'cat  {} |'
                                              'awk -F"\\t" \'NR>1 {{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' '
                                              '>> {}'.format(input_file, sample_id, output_file), verb))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing Segmented format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_hmmcopy_tsv(exports_config: Config.Config, study_config: Config.Config, verb):

    # Gather ingredients
    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    seg_temp = helper.get_temp_folder(output_folder, 'seg')

    bed_filter = subprocess.check_output(['awk "NR>1" {} | '
                                          'awk -F"\\t" \'{{print $1}}\' | '
                                          'uniq'.format(exports_config.config_map['bed_file'])],
                                         shell=True).decode("utf-8")

    bed_filter = bed_filter.strip().split('\n')
    bed_filter = bed_filter + ['chr' + a for a in bed_filter]
    bed_filter = ['\\t' + a + '\\t' for a in bed_filter]

    header = 'ID\\tchrom\\tloc.start\\tloc.end\\tnum.mark\\tseg.mean'
    helper.call_shell('head {}'.format(os.path.join(input_folder, export_data['FILE_NAME'][0])), verb)
    # Cook
    for i in range(len(export_data)):
        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(seg_temp, export_data['FILE_NAME'][i])
        sample_id = export_data['TUMOR_ID'][i]

        helper.working_on(verb, 'Refactoring cols: {}'.format(export_data['FILE_NAME'][i]))
        if  input_file == output_file:
            output_temp = output_file + '.temp'

            calls.append(helper.parallel_call('echo "{}" > {}; '.format(header, output_temp) +
                                              'cat  {} | '
                                              'awk \'BEGIN{{split("{}",t); for (i in t) vals[t[i]]}} ($2 in vals)\' | '
                                              'awk -F"\\t" \'{{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' >> '
                                              '{}; '.format(input_file, '|'.join(bed_filter), sample_id, output_temp) +
                                              'mv {} {}'.format(output_temp, output_file),
                                              verb))
        else:
            calls.append(helper.parallel_call('echo "{}" > {}; '.format(header, output_file) +
                                              'cat  {} | '
                                              'awk \'BEGIN{{split("{}",t); for (i in t) vals[t[i]]}} ($2 in vals)\' | '
                                              'awk -F"\\t" \'{{ OFS="\\t"; print "{}", $2, $3, $4, $5, $6}}\' >> '
                                              '{} '.format(input_file, '|'.join(bed_filter), sample_id, output_file),
                                              verb))
    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    helper.call_shell('head {}'.format(os.path.join(input_folder, export_data['FILE_NAME'][0])), verb)

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing HMMCopy format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def fix_hmmcopy_max_chrom(exports_config: Config.Config, study_config: Config.Config, verb):

    calls = []
    output_folder = study_config.config_map['output_folder']
    input_folder = exports_config.config_map['input_folder']
    export_data = exports_config.data_frame
    seg_temp = helper.get_temp_folder(output_folder, 'seg')
    helper.call_shell('head {}'.format(os.path.join(input_folder, export_data['FILE_NAME'][0])), verb)

    # Cook
    for i in range(len(export_data)):

        input_file = os.path.join(input_folder, export_data['FILE_NAME'][i])
        output_file = os.path.join(seg_temp, export_data['FILE_NAME'][i])
        dictionary = os.path.abspath(os.path.join(os.path.dirname(__file__), '../constants/' + constants.hmmcopy_chrom_positions))

        if  input_file == output_file:
            output_temp = output_file + '.temp'

            calls.append(helper.parallel_call("awk -F'\\t' 'BEGIN {{OFS = FS}} FNR==NR {{dict[$1]=$2; next}} "
                                              "FNR >= 2 {{$4=($4 in dict) ? dict[$4] : $4; $5=int(($4-$3)/1000)}}1' {} {}"
                                              "> {};".format(dictionary, input_file, output_temp) +
                                              'mv {} {}'.format(output_temp, output_file), verb))

        else:
            calls.append(helper.parallel_call("awk -F'\\t' 'BEGIN {{OFS = FS}} FNR==NR {{dict[$1]=$2; next}} "
                                              "NR >  1 {{$4=($4 in dict) ? dict[$4] : $4; $5=int(($4-$3)/1000)}}1' {} {}"
                                              "> {} ".format(dictionary, input_file, output_file), verb))

    exports_config.config_map['input_folder'] = seg_temp
    # Wait until Baked
    exit_codes = [p.wait() for p in calls]
    helper.call_shell('head {}'.format(os.path.join(input_folder, export_data['FILE_NAME'][0])), verb)

    # Clean up
    if any(exit_codes):
        raise ValueError('ERROR:: Something went wrong when parsing HMMCopy format file? Please resolve the issue')
    if verb:
        print(exit_codes)


def gen_cna(exports_config: Config.Config, study_config: Config.Config, verb):
    # TODO:: Run Rscript to generate CNA and log2CNA files from concated SEG file

    helper.working_on(verb, message='Gathering files ...')
    seg_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config]))
    bed_file = exports_config.config_map['bed_file']
    l_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config + '_LOG2CNA']))
    c_o_file = os.path.join(study_config.config_map['output_folder'],
                            'data_{}.txt'.format(constants.config2name_map[exports_config.type_config + '_CNA']))

    helper.working_on(verb, message='Generating log2CNA...')

    # This may break if after loading the module R-gsi/3.5.1, Rscript is not set as a constant
    helper.call_shell('Rscript lib/data_type/seg2gene.R '
                      '-s {} '
                      '-g {} '
                      '-o {} '.format(seg_file, bed_file, l_o_file), verb)

    helper.working_on(verb, message='Generating CNA...')
    helper.call_shell('awk -f lib/data_type/log2CNA.awk -v gain=0.3 ampl=0.7 htzd=-0.3 hmzd=-0.7 {} | '
                      'sed \'s/[[:blank:]]*$//\' > {}'.format(l_o_file, c_o_file), verb)
