"""Config files for components of a cBioPortal study"""

import logging
import os
from math import inf as infinity

from utilities.config import config, ConfigError
import utilities.constants

class generation_config(config):
    """base class for study generation config"""

    def __init__(self, input_path, log_level=logging.WARNING, strict=False):
        name = "%s.%s" % (__name__, type(self).__name__)
        super().__init__(input_path, log_level, name, strict)

class cancer_type_config(generation_config):
    """cBioPortal cancer type config"""
    pass

class case_list_config(generation_config):

    def get_sample_ids(self):
        return self.table['SAMPLE_ID'].tolist()

class clinical_config(generation_config):
    """Clinical sample/patient config"""

    DISPLAY_NAMES_KEY = 'display_names'
    DESCRIPTIONS_KEY = 'descriptions'
    DATATYPES_KEY = 'datatypes'
    PRIORITIES_KEY = 'priorities'
    STRING_TYPE = 'STRING'
    NUMBER_TYPE = 'NUMBER'
    BOOLEAN_TYPE = 'BOOLEAN'

    # TODO check validity of table body

    def __init__(self, input_path, log_level=logging.WARNING, strict=False):
        super().__init__(input_path, log_level, strict)
        self.PATIENT_DATATYPE = utilities.constants.PATIENT_DATATYPE
        self.SAMPLE_DATATYPE = utilities.constants.SAMPLE_DATATYPE

    def is_valid_type(self, type_string):
        return type_string in [self.STRING_TYPE, self.NUMBER_TYPE, self.BOOLEAN_TYPE]

    def get_clinical_headers(self):
        display_names = self.meta[self.DISPLAY_NAMES_KEY]
        descriptions = self.meta[self.DESCRIPTIONS_KEY]
        datatypes = self.meta[self.DATATYPES_KEY]
        priorities = self.meta[self.PRIORITIES_KEY]
        columns = len(display_names)
        if len(descriptions)!=columns or len(datatypes)!=columns or len(priorities)!=columns:
            msg = "Inconsistent number of column fields in metadata"
            raise ConfigError(msg)
        for datatype in datatypes:
            if not self.is_valid_type(datatype):
                msg = "Type %s is not a valid cBioPortal datatype" % datatype
                self.logger.error(msg)
                raise ConfigError(msg)
        for priority in priorities:
            try:
                num = int(priority)
            except ValueError as ve:
                msg = "Priority '%s' is not an integer: {0}".format(ve)
                self.logger.error(msg)
                raise ConfigError(msg)
        return [display_names, descriptions, datatypes, priorities]

class pipeline_config(generation_config):
    """Config for a pipeline component corresponding to a cBioPortal datatype"""
    pass

class study_config(generation_config):
    """cBioPortal study config in Janus format"""

    RESERVED_DATATYPES = [
        utilities.constants.CASE_LIST_DATATYPE,
        utilities.constants.CANCER_TYPE_DATATYPE,
        utilities.constants.PATIENT_DATATYPE,
        utilities.constants.SAMPLE_DATATYPE
    ]

    def __init__(self, input_path, log_level=logging.WARNING, strict=False):
        super().__init__(input_path, log_level, strict)
        self.logger = self.get_logger(log_level, __name__) # more specific logger name

    def get_cancer_study_identifier(self):
        return self.meta['cancer_study_identifier']

    def get_config_paths_by_datatype(self, datatype, required_min=0, allowed_max=infinity):
        """Get config paths for a given datatype; raise error if total found is incorrect"""
        dt_frame = self.table.loc[self.table['DATAHANDLER']==datatype]
        total_rows = len(dt_frame.index)
        if total_rows < required_min:
            msg = "Expected at least %i rows for datatype %s, found %i" \
                  % (required_min, datatype, total_rows)
            self.logger.error(msg)
            raise ValueError(msg)
        elif total_rows > allowed_max:
            msg = "Expected at most %i rows for datatype %s, found %i" \
                  % (allowed_max, datatype, total_rows)
            self.logger.error(msg)
            raise ConfigError(msg)
        config_paths = []
        for i in range(total_rows):
            filename = dt_frame.iloc[i]['FILE_NAME']
            config_paths.append(os.path.join(self.config_dir, filename))
        return config_paths

    def get_single_config_path_by_datatype(self, datatype, required=False):
        """Find a config path expected to occur at most once"""
        if required:
            required_min = 1
        else:
            required_min = 0
        paths = self.get_config_paths_by_datatype(datatype, required_min, allowed_max=1)
        if len(paths) > 0:
            path = paths[0]
        else:
            path = None
        return path

    def get_case_list_config_paths(self):
        return self.get_config_paths_by_datatype(utilities.constants.CASE_LIST_DATATYPE)

    def get_cancer_type_config_path(self):
        return self.get_single_config_path_by_datatype(utilities.constants.CANCER_TYPE_DATATYPE)

    def get_patient_config_path(self):
        return self.get_single_config_path_by_datatype(utilities.constants.PATIENT_DATATYPE)

    def get_alterationtype_config_paths(self):
        """Return a dictionary of dictionaries of config paths, indexed by alteration and data type"""
        reserved = set(self.RESERVED_DATATYPES)
        at_key = utilities.constants.ALTERATION_TYPE_KEY
        dh_key = utilities.constants.DATAHANDLER_KEY
        config_paths = {}
        for index, row in self.table.iterrows():
            alteration_type = row[at_key]
            datahandler = row[dh_key]
            file_name = row[utilities.constants.FILE_NAME_KEY]
            if datahandler in reserved:
                continue
            if alteration_type not in config_paths:
                config_paths[alteration_type] = {}
            if datahandler in config_paths[alteration_type]:
                msg = "Combination of {0} and {1} is not unique: {2}, {3}".format(
                    at_key, dh_key, alteration_type, datahandler
                )
                self.logger.error(msg)
                raise ConfigError(msg)
            config_paths[alteration_type][datahandler] = os.path.join(self.config_dir, file_name)
        return config_paths

    def get_sample_config_path(self):
        # sample config is required
        return self.get_single_config_path_by_datatype(utilities.constants.SAMPLE_DATATYPE, True)
