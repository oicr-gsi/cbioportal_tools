"""Config files for components of a cBioPortal study"""

import os
import sys

from utilities.config import config
import utilities.constants

class cancer_type_config(config):
    """cBioPortal cancer type config"""
    pass

class clinical_config(config):
    """Clinical sample/patient config"""

    DISPLAY_NAMES_KEY = 'display_names'
    DESCRIPTIONS_KEY = 'descriptions'
    DATATYPES_KEY = 'datatypes'
    PRIORITIES_KEY = 'priorities'
    STRING_TYPE = 'STRING'
    NUMBER_TYPE = 'NUMBER'
    BOOLEAN_TYPE = 'BOOLEAN'

    # TODO check validity of table body

    def __init__(self, input_path, strict=False):
        super().__init__(input_path, strict)
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
            raise ValueError(msg)
        for datatype in datatypes:
            if not self.is_valid_type(datatype):
                raise ValueError("Type %s is not a valid cBioPortal datatype" % datatype)
        for priority in priorities:
            try:
                num = int(priority)
            except ValueError:
                msg = "Priority '%s' is not an integer"
                print(msg, file=sys.stderr) # TODO add logger
                raise
        return [display_names, descriptions, datatypes, priorities]


class study_config(config):
    """cBioPortal study config in Janus format"""

    EXPECTED_COLUMNS = 3

    def get_cancer_study_identifier(self):
        return self.meta['cancer_study_identifier']

    def get_config_path(self, datatype):
        """General-purpose method to get the config path for a given datatype"""
        dt_frame = self.table.loc[self.table['DATAHANDLER']==datatype]
        if dt_frame.size == 0:
            # some config types are optional; return None if path is not found
            config_path = None
        else:
            filename = dt_frame.iloc[0]['FILE_NAME']
            if dt_frame.size > self.EXPECTED_COLUMNS:
                msg = "Warning: Multiple config files appear to be present "+\
                      "for %s; using first value: '%s'" % (datatype, filename)
                print(msg, file=sys.stderr) # TODO replace with logger
            config_path = os.path.join(self.config_dir, filename)
        return config_path

    def get_cancer_type_config_path(self):
        return self.get_config_path(utilities.constants.CANCER_TYPE_DATATYPE)

    def get_patient_config_path(self):
        return self.get_config_path(utilities.constants.PATIENT_DATATYPE)

    def get_sample_config_path(self):
        return self.get_config_path(utilities.constants.SAMPLE_DATATYPE)
