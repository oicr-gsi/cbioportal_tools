"""Class to represent a CSV file with YAML header"""

# See http://csvy.org/ and https://cran.r-project.org/web/packages/csvy/readme/README.html

import pandas as pd
import logging
import re
import os
import yaml

import sys # TODO FIXME

import utilities.constants
from utilities.base import base

class config(base):

    # TODO validate the CSV contents against a schema, eg. using https://pypi.org/project/csvvalidator/

    # The optional YAML header block must:
    # - be at the start of the file
    # - start and finish with a line consisting of only '...' or '---'
    # - have body lines which each start with a #
    #
    # Outwith the header, a line starting with # is treated as a comment and ignored

    REQUIRED_META_FIELDS = []
    OPTIONAL_META_FIELDS = []
    
    def __init__(self, input_path, schema_path=None, log_level=logging.WARNING, name=None, strict=False):
        if name == None:
            name = "%s.%s"% (__name__, type(self).__name__)
        self.logger = self.get_logger(log_level, name)
        if schema_path != None:
            self.schema = schema(schema_path, log_level=log_level)
        else:
            self.schema = None
        self.config_dir = os.path.abspath(os.path.dirname(input_path))
        [self.meta, skip_total] = self.read_meta(input_path)
        if strict:
            self.validate_meta_fields()
        self.table = pd.read_csv(input_path, sep="\t", comment="#", skiprows=skip_total)

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
        meta_valid = self.schema.validate_meta(self.meta)
        body_valid = self.schema.validate_table(self.table)
        return meta_valid and body_valid

    def validate_meta_paths(self):
        """Validate paths in the header"""
        if self.schema == None:
            raise JanusConfigError("Cannot validate syntax because no schema is specified")
        return self.schema.validate_meta_paths(self.header)


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

class schema(base):

    """Schema class for a Janus config file, with validation/template methods"""

    def __init__(self, schema_path, log_level=logging.WARNING):
        name = "%s.%s"% (__name__, type(self).__name__)
        self.logger = self.get_logger(log_level, name)
        with open(schema_path, 'r') as schema_file:
            schema = yaml.safe_load(schema_file.read())
        self.head = schema.get('head')
        if not self.head:
            msg = "No 'head' entry in Janus schema path '%s'" % schema_path
            self.logger.error(msg)
            raise JanusConfigError(msg)
        self.body = schema.get('body')
        if not self.body:
            msg = "No 'body' entry in Janus schema path '%s'" % schema_path
            self.logger.error(msg)
            raise JanusConfigError(msg)
        self.all_head_keys = set(self.head.keys())
        self.required_head_keys = set()
        for key in self.head.keys():
            if self.head[key].get('required'):
                self.required_head_keys.add(key)

    def _generate_header_template(self, schema_dict):
        """
        Change a schema dictionary into a Janus config header template.
        Use recursively to generate templates for dictionaries in the header.
        """
        template = {}
        for key in schema_dict.keys():
            schema_val = schema_dict.get(key)
            type_string = schema_val.get('type', 'any')
            if type_string == 'dictionary':
                template_val = self._generate_header_template(schema_val['contents'])
            elif schema_val.get('required'):
                template_val = '%s: REQUIRED' % type_string
            else:
                template_val = '%s: OPTIONAL' % type_string
            template[key] = template_val
        return template

    def validate_table(self, table):
        """validate a Pandas dataframe against the schema"""
        valid = True
        table_column_names = list(table.columns.values)
        if table_column_names != self.body:
            msg = "Input columns [%s] do not match schema columns [%s]" % (
                ', '.join(table_column_names),
                ', '.join(self.body),
            )
            self.logger.warning(msg)
            valid = False
        return valid
            
    def validate_meta(self, meta):
        """validate a header dictionary against the schema"""
        valid = True
        meta_key_set = set(meta.keys())
        missing_set = self.required_head_keys - meta_key_set
        if len(missing_set) > 0:
            missing = ', '.join(sorted(list(missing_set)))
            self.logger.warning("Missing required header fields: %s" % missing)
            valid = False
        extra_set = meta_key_set - self.all_head_keys
        if len(extra_set) > 0:
            extra = ', '.join(sorted(list(extra_set)))
            self.logger.warning("Extra fields not present in schema: %s" % extra)
            valid = False
        return valid

    def validate_meta_paths(self, meta):
        """
        Check any paths in the header dictionary exist and are readable.
        Relative paths are checked with respect to the current working directory.
        Does not (yet) check for type (file vs. directory) or writability.
        """
        valid = True
        msg = "Validating paths with respect to the current working directory %s" % os.getcwd()
        self.logger.info(msg)
        for key, val in meta:
            schema_val = self.head.get(key)
            if schema_val.get('type') == 'path':
                if not os.path.exists(val):
                    self.logger.warn("Path '%s' does not exist" % val)
                    valid = False
                elif not os.access(val, os.R_OK):
                    self.logger.warn("Path '%s' exists but is not readable" % val)
                    valid = False
        if valid:
            self.logger.info("All paths in metadata exist and are readable.")
        else:
            self.logger.warn("One or more path in metadata does not exist or is not readable.")
        return valid

    def write_template(self, out_file):
        """write a template based on the schema"""
        yaml_delimiter = '---'
        print(yaml_delimiter, file=out_file)
        header = self._generate_header_template(self.head)
        # dump header to YAML and convert to list of (non-empty) strings
        header_lines = [x for x in re.split('\n', yaml.dump(header)) if x!='']
        for line in header_lines:
            print('#'+line, file=out_file)
        print(yaml_delimiter, file=out_file)
        print('\t'.join(self.body), file=out_file)
        print('\t'.join([x.lower()+'_value' for x in self.body]), file=out_file)


class JanusConfigError(Exception):
    pass
