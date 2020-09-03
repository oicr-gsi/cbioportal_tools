"""Class to represent a CSV file with YAML header"""

# See http://csvy.org/ and https://cran.r-project.org/web/packages/csvy/readme/README.html

import pandas as pd
import logging
import re
import os
import yaml

import utilities.constants
from utilities.base import base
from utilities.schema import schema

class config(base):

    REQUIRED_META_FIELDS = []
    OPTIONAL_META_FIELDS = []
    
    def __init__(self, input_path, schema_path=None, log_level=logging.WARNING, log_name=None,
                 log_path=None):
        if log_name == None:
            log_name = "%s.%s"% (__name__, type(self).__name__)
        self.logger = self.get_logger(log_level, log_name, log_path)
        self.input_path = input_path
        if schema_path != None:
            self.schema = schema(schema_path, log_level=log_level)
        else:
            self.schema = None
        self.config_dir = os.path.abspath(os.path.dirname(input_path))
        [self.meta, skip_total] = self.read_meta(input_path)
        self.table = pd.read_csv(input_path, sep="\t", comment="#", skiprows=skip_total)
        if self.table.isnull().values.any():
            self.logger.warning("Body of %s has null values" % input_path)

    def data_as_tsv(self):
        return self.table.to_csv(sep="\t", index=False)

    def contents_equal(self, other):
        """Check if contents equal with another config"""
        try:
            equal = self.meta == other.get_meta() and self.table.equals(other.get_table())
        except AttributeError as err:
            msg = "Attribute not found. Attempting to compare with a non-config object? "+str(err)
            self.logger.error(msg)
            raise
        return equal
    
    def get_meta(self):
        return self.meta

    def get_meta_value(self, key):
        """return meta[key] if present, None otherwise"""
        return self.meta.get(key)

    def get_table(self):
        return self.table

    def read_meta(self, input_path):
        yaml_lines = []
        line_count = 0
        skip_rows = 0 # number of header rows to skip
        with open(input_path) as in_file:
            body = False
            boundary_expr = re.compile('^(\.\.\.)|(---)$') # no regex quantifiers; avoids FutureWarning
            for line in in_file.readlines():
                line_count += 1
                if line_count == 1:
                    if boundary_expr.match(line):
                        skip_rows = 1
                        body = True
                    else:
                        break
                elif body:
                    skip_rows += 1
                    if re.match('#', line):
                        yaml_lines.append(line.lstrip('#'))
                    elif boundary_expr.match(line):
                        body = False
                        break
                    else:
                        msg = "Lines in YAML header should begin with #"
                        self.logger.error(msg)
                        raise JanusConfigError(msg)
            if body:
                msg = "YAML header section opened with ... or ---, but never closed"
                self.logger.error(msg)
                raise JanusConfigError(msg)
        meta = yaml.safe_load(''.join(yaml_lines))
        return (meta, skip_rows)

    def validate_syntax(self):
        """Validate header and body syntax against the schema"""
        if self.schema == None:
            raise JanusConfigError("Cannot validate syntax because no schema is specified")
        if self.schema.has_head():
            meta_valid = self.schema.validate_meta(self.meta, os.path.basename(self.input_path))
        else:
            self.logger.info("No header specified in schema, omitting metadata validation")
            meta_valid = True
        body_valid = self.schema.validate_table(self.table, os.path.basename(self.input_path))
        valid = meta_valid and body_valid
        if valid:
            self.logger.info("Config syntax for %s is valid" % self.input_path)
        else:
            self.logger.warning("Config syntax for %s IS NOT valid" % self.input_path)
        return valid

class legacy_config_wrapper(base):

    """duplicates functionality of legacy Config.Config on a utilities.config object"""
    def __init__(self, config, alt_type, data_type, log_level=logging.WARNING, name=None, strict=False):
        if name == None:
            name = "%s.%s"% (__name__, type(self).__name__)
        self.logger = self.get_logger(log_level, name)
        self.config = config
        # duplicate attributes of the legacy config class
        self.analysis = alt_type
        self.type_config = data_type
        self.config_map = config.get_meta()
        self.data_frame = config.get_table()
        self.alterationtype = alt_type
        self.data_type = data_type # TODO clarify datatype/handler terminology
        self.datahandler = self.config_map.get(utilities.constants.DATATYPE_KEY)


    def set_config_mapping(self, k, v):
        """Update a key/value pair in the metadata map; eg. the study output path"""
        self.config_map[k] = v

    def __str__(self):
        return str([self.config_map, self.data_frame, self.datahandler, self.alterationtype])


class JanusConfigError(Exception):
    pass

