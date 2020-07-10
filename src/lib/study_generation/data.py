"""Manipulate study generation data"""

import logging
import os

import numpy as np
import pandas as pd

from lib.constants.constants import config2name_map
#from lib.data_type import cancer_type
#from lib.data_type.SEG import segmented_data
#from lib.data_type.MAF import mutation_data
#from lib.data_type.CONTINUOUS_COPY_NUMBER import continuous_copy_number_data
#from lib.data_type.DISCRETE_COPY_NUMBER import discrete_copy_number_data
from lib.support import Config, helper

from lib.analysis_pipelines import cancer_type
from lib.analysis_pipelines.COPY_NUMBER_ALTERATION import support_functions
from lib.analysis_pipelines.MUTATION_EXTENDED import support_functions
from lib.analysis_pipelines.MRNA_EXPRESSION import support_functions

from lib.support import Config, helper



def assert_format(meta_config: Config.Config, verb):
    helper.working_on(verb, message='Asserting correct file format for {} file ... '.format(meta_config.type_config))

    if   meta_config.type_config == 'MAF':
        mutation_data.verify_final_file(meta_config, verb)

    elif meta_config.type_config == 'SEG':
        segmented_data.verify_final_file(meta_config, verb)

    elif meta_config.type_config == 'CONTINUOUS_COPY_NUMBER':
        continuous_copy_number_data.verify_final_file(meta_config, verb)

    elif meta_config.type_config == 'DISCRETE_COPY_NUMBER':
        discrete_copy_number_data.verify_final_file(meta_config, verb)


def generate_data_type(meta_config: Config.Config, study_config: Config.Config, logger: logging.Logger):

    # janus_path is the root path of the cbioportal_tools repo
    # TODO get rid of command-line execution of other scripts, and with it the need for janus_path
    study_gen_dir = os.path.dirname((os.path.abspath(__file__)))
    janus_path = os.path.abspath(os.path.join(study_gen_dir, os.pardir, os.pardir, os.pardir))

    verb = logger.isEnabledFor(logging.INFO) # TODO replace the 'verb' switch with calls to a logger

    ### READ DIRECTLY FROM THE FILE, NO OTHER ACTION
    if 'pipeline' in meta_config.config_map.keys() and meta_config.config_map['pipeline'] == 'FILE':
        #TODO:: Assert correct format for all data types...
        assert_format(meta_config, verb)

        helper.copy_file(os.path.join(meta_config.config_map['input_folder'],
                                      meta_config.data_frame['FILE_NAME'][0]),
                         os.path.join(study_config.config_map['output_folder'],
                                      'data_{}.txt'.format(config2name_map[meta_config.type_config])),
                         verb)

    elif meta_config.datahandler == 'CANCER_TYPE':
        logger.debug('Started reading colours')
        colours = cancer_type.get_colours(janus_path)
        logger.debug('Finished reading colours')

        logger.debug('Started generating CANCER_TYPE records')
        cancer_type.gen_cancer_type_data(meta_config, study_config, colours)
        logger.debug('Finished generating CANCER_TYPE records')

    else:
        helper.assert_type(meta_config.alterationtype)
        logger.info('Pipeline is {}, beginning preparation.'.format(meta_config.config_map['pipeline']))
        helper.assert_pipeline(meta_config.alterationtype, meta_config.config_map['pipeline'])
        pipeline = os.path.abspath(os.path.join(janus_path,
                                                'src/lib/analysis_pipelines/{}/{}.py'.format(meta_config.alterationtype,
                                                                                    meta_config.config_map['pipeline'])))
        helper.execfile(pipeline,
                        {'meta_config':meta_config,
                         'study_config':study_config,
                         'janus_path':janus_path,
                         'verb':verb})


def get_sample_ids(meta_config: Config.Config, verb) -> pd.Series:
    helper.working_on(verb, message='Getting Sample IDs of {} from FILE pipeline...'.format(meta_config.type_config))

    ids = []
    # TODO:: Gather Sample_IDs from other data_types as well ...
    # This is important to do for the case_lists that need to be generated.

    if   meta_config.type_config == 'MAF':
        ids = mutation_data.get_sample_ids(meta_config, verb)

    elif meta_config.type_config == 'SEG':
        ids = segmented_data.get_sample_ids(meta_config, verb)

    return ids


def generate_data_clinical(samples_config: Config.ClinicalConfig, study_config: Config.Config, verb):
    print(samples_config)
    num_header_lines = 4
    helper.working_on(verb, message='Writing to data_{}.txt ...'.format(config2name_map[samples_config.alterationtype + ":" + samples_config.datahandler]))

    output_file = os.path.join(os.path.abspath(study_config.config_map['output_folder']),
                               'data_{}.txt'.format(config2name_map[samples_config.alterationtype + ":" + samples_config.datahandler]))

    array = np.array(samples_config.data_frame)

    f = open(output_file, 'w')
    for i in range(array.shape[0]):
        if i < num_header_lines:
            f.write('#{}\n'.format('\t'.join(samples_config.data_frame[i])))
        else:
            f.write('{}\n'.format('\t'.join(samples_config.data_frame[i])))
    f.flush()
    f.close()
    helper.working_on(verb)
