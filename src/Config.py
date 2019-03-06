import pandas as pd
import os


class Config(object):
    config_map: dict = {}
    data_frame: pd.DataFrame = pd.DataFrame()
    type_config: str = ''

    def __init__(self, config_map: dict, data_frame: pd.DataFrame, type_config: str):
        self.config_map = config_map.copy()
        self.data_frame = data_frame.copy()
        self.type_config = type_config

    @classmethod
    def from_config(cls, config):
        return cls(config.config_map, config.data_frame, config.type_config)

    def __str__(self):
        return str([self.config_map, self.data_frame, self.type_config])


class ClinicalConfig(Config):
    data_frame: list

    def __init__(self, config_map: dict, array, type_config: str):
        self.config_map = config_map
        self.data_frame = array
        self.type_config = type_config


def get_config(file, f_type, verb) -> Config:
    if os.path.isfile(file):
        print('File Name: {}'.format(file))
    else:
        raise OSError('ERROR: Is not a file\n' + file)
    f = open(file, 'r')

    print('Reading information') if verb else print(),
    file_map = {}
    for line in f:
        if line[0] == '#':
            line = line.strip().replace('#', '').split('=')
            file_map[line[0]] = line[1]
        else:
            break
    f.close()
    data_frame = pd.read_csv(file, delimiter='\t', skiprows=len(file_map), dtype=object)

    config_file = Config(file_map, data_frame, f_type)
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
