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
        [self.meta, skip_total] = self.read_meta(input_path)
        if strict:
            self.validate_meta_fields()
        self.table = pd.read_csv(input_path, sep="\t", comment="#", skiprows=skip_total)

    def data_as_tsv(self):
        return self.table.to_csv(sep="\t", index=False)

    def get_meta(self):
        return self.meta

    def read_meta(self, input_path):
        yaml_lines = []
        with open(input_path) as in_file:
            body = False
            boundary_expr = re.compile('^(\.\.\.)|(---)$') # no regex quantifiers; avoids FutureWarning
            skiprows = 0 # number of header rows to skip when reading TSV
            for line in in_file.readlines():
                if body == False and boundary_expr.match(line):
                    body = True
                    skiprows = 1
                elif body:
                    skiprows += 1
                    if re.match('#', line):
                        yaml_lines.append(line.lstrip('#'))
                    elif boundary_expr.match(line):
                        break
                    else:
                        raise ConfigError("Lines in YAML header should begin with #")
        meta = yaml.safe_load(''.join(yaml_lines))
        return (meta, skiprows)

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

class ConfigError(Exception):
    pass
