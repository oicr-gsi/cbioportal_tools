"""Class to represent a CSV file with YAML header"""

# See http://csvy.org/ and https://cran.r-project.org/web/packages/csvy/readme/README.html

import pandas as pd
import re
import os
import sys
import yaml

class config:

    # TODO validate the CSV contents against a schema, eg. using https://pypi.org/project/csvvalidator/

    REQUIRED_META_FIELDS = []
    OPTIONAL_META_FIELDS = []
    
    def __init__(self, input_path, strict=False):
        self.config_dir = os.path.abspath(os.path.dirname(input_path))
        self.meta = self.read_meta(input_path)
        if strict:
            self.validate_meta_fields()
        self.table = pd.read_csv(input_path, sep="\t", comment="#")

    def data_as_tsv(self):
        return self.table.to_csv(sep="\t", index=False)

    def get_cancer_study_identifier(self):
        return self.meta['cancer_study_identifier']

    def get_sample_config_path(self):
        filename = self.table.loc[self.table['DATAHANDLER']=='SAMPLE_ATTRIBUTES'].at[0, 'FILE_NAME']
        return os.path.join(self.config_dir, filename)
        
    def read_meta(self, input_path):
        yaml_lines = []
        with open(input_path) as in_file:
            body = False
            for line in in_file.readlines():
                if re.match('#', line):
                    yaml_lines.append(line.lstrip('#'))
                else:
                    break
        return yaml.safe_load(''.join(yaml_lines))

    def validate_meta_fields(self):
        missing_required = []
        for field in self.REQUIRED_META:
            if not self.meta.has_key(field):
                missing_required.append(field)
        expected_fields = set()
        expected_fields.update(self.REQUIRED_META)
        expected_fields.update(self.OPTIONAL_META)
        unexpected = []
        for field in self.meta.keys():
            if field not in self.expected_fields():
                unexpected.append(field)
        if len(unexpected) > 0:
            msg = 'Unexpected metadata fields found: '+', '.join(unexpected)
            print(msg, file=sys.stderr) # TODO add a logger; warn
        if len(missing_required) > 0:
            msg = 'Missing required metadata fields: '+', '.join(missing_required)
            print(msg, file=sys.stderr) # TODO add a logger; error
            raise ConfigError(msg)

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


class ConfigError(Exception):
    pass
