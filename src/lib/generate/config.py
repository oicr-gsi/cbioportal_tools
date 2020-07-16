"""Config files for components of a cBioPortal study"""

import sys

from utilities.config import config

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
    pass
