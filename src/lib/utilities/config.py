"""Class to represent a CSV file with YAML header"""

# See http://csvy.org/ and https://cran.r-project.org/web/packages/csvy/readme/README.html

import pandas as pd
import re
import sys
import yaml

class config:

    # TODO validate the CSV contents against a schema, eg. using https://pypi.org/project/csvvalidator/

    REQUIRED_META_FIELDS = []
    OPTIONAL_META_FIELDS = []
    
    def __init__(self, input_path, strict=False):
        self.meta = self.read_meta(input_path)
        self.table = pd.read_csv(input_path, sep="\t", comment="#")
        if strict:
            self.validate_meta_fields()
        
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
            raise CSVYError(msg)

class CSVYError(Exception):
    pass
