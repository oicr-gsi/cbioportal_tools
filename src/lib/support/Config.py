__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

# Command line imports
import os
import typing
import argparse

import pandas as pd
from ..constants.constants import clinical_type, no_data_frame


class Config(object):
    config_map: dict = {}
    data_frame: pd.DataFrame
    type_config: str = ''
    analysis: str = ''

    def __init__(self, config_map: dict, data_frame: pd.DataFrame, datatype: str, alterationtype: str):
        self.config_map = config_map.copy()
        self.data_frame = data_frame.copy()
        self.datatype = datatype
        self.alterationtype = alterationtype

    @classmethod
    def from_config(cls, config):
        return cls(config.config_map, config.data_frame, config.datatype, config.alterationtype)

    def __str__(self):
        return str([self.config_map, self.data_frame, self.datatype, self.alterationtype])


class ClinicalConfig(Config):
    data_frame: list

    def __init__(self, config_map: dict, array, datatype: str):
        self.config_map = config_map
        self.data_frame = array
        self.datatype = datatype
        self.alterationtype = "CLINICAL"


Information = typing.List[Config]

### loads the study configuration from a file
def get_single_config(file, f_type, analysis, verb) -> Config:

    ### verify that the file exists
    if os.path.isfile(file):
        print('File Name: {}'.format(file))
    else:
        raise OSError('ERROR: Is not a file\n' + file)
    ### open the filehandle
    f = open(file, 'r')

    print('Reading information') if verb else print(),
    file_map = {}
    line = ''

    ### commented out header lines are key value pairs, these are stored in the file_map
    try:
        for line in f:#TypeError: get_single_config() missing 1 required positional argument: 'verb'
            if line[0] == '#':
                line = line.strip().replace('#', '').split('=')
                file_map[line[0]] = line[1]
            else:
                ### break if not a comment line, the rest is a data table.  should not be any more comment lines
                break
        f.flush()
        f.close()
    except IndexError:
        print('ERROR:: there was a syntax error in the header of {}'.format(file))
        print(line)
        exit(1)

    ### now read in the data table, it should be tab delimited
    ## this is stored in data_frame
    try:
        data_frame = pd.read_csv(file, delimiter='\t', skiprows=len(file_map), dtype=str)
    except pd.errors.EmptyDataError:
        if f_type in no_data_frame:
            data_frame = pd.DataFrame()
        else:
            print('Your {} file does not have data in it but it probably should, please double check it'.format(f_type))
            raise pd.errors.EmptyDataError()

    ### check that it loaded properly
    if data_frame.isnull().values.any():
        print('ERROR:: A configuration file is missing some values in the data-frame, this is not right.')
        print('Check this file {}'.format(file))
        exit(1)

    ### store all information in a config object, with properties config_map and data_frame
    config_file = Config(file_map, data_frame, f_type, analysis)
    return config_file


def get_config_clinical(file: str, f_type: str, verb) -> ClinicalConfig:
    if os.path.isfile(file):
        print('Configuration File Name: {}'.format(file))
    else:
        raise OSError('ERROR: Is not a file\n' + file)
    f = open(file, 'r')

    print('Reading information') if verb else print(),
    file_map = {}
    data_frame = []
    for line in f:
        if line[0] == '#':
            line = line.strip().replace('#', '').split('=')
            file_map[line[0]] = line[1]
        else:
            data_frame.append(line.strip().split('\t'))
    config_file = ClinicalConfig(file_map, data_frame, f_type)
    return config_file

### once the config is into the study_config object, parse and store the information in other objecgts
def gather_config_set(study_config: Config, args: argparse.Namespace, verb) -> [Information, Config, Information]:
    information = []
    clinic_data = []
    custom_list = []

    # Gather the list of config files from the data frame, for each analysis and type
    for i in range(study_config.data_frame.shape[0]):
        config_file_name = os.path.join(os.path.dirname(os.path.abspath(args.config)),
                                        str(study_config.data_frame['FILE_NAME'][i]))

        config_file_type = study_config.data_frame['DATATYPE'][i]
        config_analysis = study_config.data_frame['ALTERATIONTYPE'][i]

        #### is the type one of the clinical types?
        if   study_config.data_frame['DATATYPE'][i] in clinical_type:
            clinic_data.append(get_config_clinical(config_file_name,
                                                   config_file_type,
                                                   verb))

        ### is it a case list
        elif study_config.data_frame['DATATYPE'][i] == 'CASE_LIST':
            custom_list.append(get_single_config(config_file_name,
                                                 config_file_type,
                                                 config_analysis,
                                                 verb))
            print("MAKE CUSTOM_LIST WITHIN CONFIG.PY MAKE CUSTOM_LIST WITHIN CONFIG.PY MAKE CUSTOM_LIST WITHIN CONFIG.PY MAKE CUSTOM_LIST WITHIN CONFIG.PY MAKE CUSTOM_LIST WITHIN CONFIG.PY")
        else:
            information.append(get_single_config(config_file_name,
                                                 config_file_type,
                                                 config_analysis,
                                                 verb))

    return [information, clinic_data, custom_list]
