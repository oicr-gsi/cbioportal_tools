import pandas as pd


class Config:
    config_map: map = {}
    data_frame: pd.DataFrame = pd.DataFrame()
    type_config: str = ''

    def __init__(self, config_map, data_frame, type_config):
        self.config_map = config_map
        self.data_frame = data_frame
        self.type_config = type_config

    def __str__(self):
        return str([self.config_map, self.data_frame, self.type_config])
