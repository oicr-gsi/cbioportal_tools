import pandas as pd


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