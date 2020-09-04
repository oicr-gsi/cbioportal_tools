"""Schema for Janus config files"""

import logging
import re
import yaml

from utilities.base import base

class schema(base):

    """Schema class for a Janus config file, with validation/template methods"""

    BODY = 'body'
    CONTENTS = 'contents'
    DESCRIPTION = 'description'
    HEAD = 'head'
    LEAF = '_LEAF_' # reserved key for representing schema structure
    REQ = '_REQUIRED_' # reserved key for representing schema structure
    REQUIRED = 'required'
    TYPE = 'type'
    TYPE_RESERVED = '_TYPE_'

    DICT_TYPE = 'dictionary'
    LIST_TYPE = 'constant_list'
    SCALAR_TYPE = 'scalar'
    PERMITTED_TYPES = [DICT_TYPE, LIST_TYPE, SCALAR_TYPE]
    UNKNOWN_FILE = 'UNKNOWN_JANUS_CONFIG_FILE'

    def __init__(self, schema_path, log_level=logging.WARNING, log_path=None):
        name = "%s.%s"% (__name__, type(self).__name__)
        self.logger = self.get_logger(log_level, name, log_path)
        with open(schema_path, 'r') as schema_file:
            schema = yaml.safe_load(schema_file.read())
        self.body = schema.get(self.BODY)
        if not self.body:
            msg = "No 'body' entry in Janus schema path '%s'" % schema_path
            self.logger.error(msg)
            raise JanusSchemaError(msg)
        self.head = schema.get(self.HEAD, None)
        if self.head:
            self.permitted_head_keys = self._parse_schema_header(self.head, required_only=False)
            self.logger.debug("Permitted head keys:\n"+yaml.dump(self.permitted_head_keys))
            self.required_head_keys = self._parse_schema_header(self.head, required_only=True)
            self.logger.debug("Required head keys:\n"+yaml.dump(self.required_head_keys))
        else:
            self.logger.info("No 'head' entry in Janus schema path '%s'" % schema_path)
            self.required_head_keys = {}
            self.permitted_head_keys = {}

    def _check_permitted_keys(self, meta, permitted_keys, input_name, ancestors=''):
        """
        Recursively check if only permitted keys are present
        If an unauthorised key is found, log its name and ancestors in the tree structure
        """
        valid = True
        for key, val in meta.items():
            key_location = ancestors+':'+key
            if permitted_keys.get(key):
                permitted_val = permitted_keys[key]
                if permitted_val.get(self.TYPE_RESERVED) == self.LIST_TYPE:
                    self.logger.debug("Checking contents of list key %s" % key)
                    expected = permitted_val.get(self.CONTENTS)
                    found = val.get(self.CONTENTS)
                    if expected != found:
                        msg = "List contents do not match; expected "+\
                              "%s, found %s" % (str(expected), str(found))
                        self.logger.warning(msg)
                        valid = False
                else:
                    self.logger.debug("Recursively checking dictionary key %s" % key)
                    next_valid = self._check_permitted_keys(val,
                                                            permitted_keys[key],
                                                            input_name,
                                                            key_location)
                    valid = valid and next_valid
            elif key in permitted_keys[self.LEAF]:
                self.logger.debug('Found permitted scalar '+key_location)
            else:
                msg = "Unexpected key %s found in %s" % (key_location, input_name)
                self.logger.warning(msg)
                valid = False
        return valid

    def _check_required_keys(self, meta, required_keys, input_name, ancestors=''):
        """
        Recursively check if all required keys are present
        If a key is missing, log its name and ancestors in the tree structure
        """
        valid = True
        for key, val in required_keys.items():
            if key == self.LEAF:
                for required_key in val:
                    if not meta.get(required_key):
                        key_location = ancestors+':'+required_key
                        msg = "Required scalar %s is not present in %s" % \
                              (key_location, input_name)
                        self.logger.warning(msg)
                        valid = False
            elif key == self.REQ or key == self.TYPE_RESERVED:
                pass
            elif key not in meta:
                key_location = ancestors+':'+key
                if val.get(self.TYPE_RESERVED) == self.LIST_TYPE:
                    msg = "Required list '%s' not present" % key_location
                    self.logger.warning(msg)
                    valid = False
                elif val[self.REQ]:
                    msg = "Required dictionary '%s' not present" % key_location
                    self.logger.warning(msg)
                    valid = False
                else:
                    msg = "Optional dictionary "+\
                          "'%s' not present, omitting downstream checks" % key_location
                    self.logger.info(msg)
            elif val.get(self.TYPE_RESERVED) == self.LIST_TYPE:
                expected = val.get(self.CONTENTS)
                found = meta.get(key).get(self.CONTENTS)
                if expected != found:
                    msg = "List contents do not match; expected "+\
                          "%s, found %s" % (str(expected), str(found))
                    self.logger.warning(msg)
                    valid = False
            else:
                next_ancestors = ancestors+':'+key
                next_valid = self._check_required_keys(meta[key], val, input_name, next_ancestors)
                valid = valid and next_valid
        return valid

    def _generate_header_template(self, schema_dict, describe=False):
        """
        Change a schema dictionary into a Janus config header template.
        Use recursively to generate templates for dictionaries in the header.
        """
        template = {}
        for key in schema_dict.keys():
            schema_val = schema_dict.get(key)
            type_string = schema_val.get(self.TYPE)
            if type_string == None:
                raise JanusSchemaError("'type' must be specified for all schema entries")
            elif type_string == self.DICT_TYPE:
                template_val = self._generate_header_template(schema_val[self.CONTENTS], describe)
            else:
                if schema_val.get(self.REQUIRED):
                    template_val = '%s: REQUIRED' % type_string
                else:
                    template_val = '%s: OPTIONAL' % type_string
                if describe and schema_val.get(self.DESCRIPTION):
                    template_val = '%s: %s' % (template_val, schema_val.get(self.DESCRIPTION))
            template[key] = template_val
        return template

    def _parse_schema_header(self, schema_dict, required_only=True):
        """Recursively generate a structure of all/required keys and check for errors"""
        for key in [self.LEAF, self.REQ, self.TYPE_RESERVED]:
            if key in schema_dict.keys():
                msg = "Reserved key %s cannot be used in schema YAML" % key
                self.logger.error(msg)
                raise JanusSchemaError(msg)
        parsed = {}
        leaf_keys = [] # 'leaf' keys have values with no children, ie. scalars
        try:
            items = schema_dict.items()
        except AttributeError as err:
            msg = "Expected dictionary, found other object type; malformed Janus schema? "+str(err)
            self.log.error(msg)
            raise JanusSchemaError(msg)
        for (key, value) in items:
            value_type = value.get(self.TYPE)
            error_msg = None
            if value_type == None:
                error_msg = "No type string specified"
            elif not value_type in self.PERMITTED_TYPES:
                error_msg = "Illegal type: %s" % str(value_type)
            elif value_type in [self.DICT_TYPE, self.LIST_TYPE] and self.CONTENTS not in value:
                error_msg = "No contents specified for dictionary/list"
            if error_msg:
                self.logger.error(error_msg)
                raise JanusSchemaError(error_msg)
            # sanity checks passed, proceed with parsing
            if value_type == self.DICT_TYPE:
                if not self.CONTENTS in value:
                    msg = "No contents specified for dictionary key %s" % key
                    self.logger.error(msg)
                    raise JanusSchemaError(msg)
                parsed[key] = self._parse_schema_header(value.get(self.CONTENTS), required_only)
                parsed[key][self.TYPE_RESERVED] = self.DICT_TYPE
                parsed[key][self.REQ] = value.get(self.REQUIRED, False) # is dictionary required?
            elif required_only == False or value.get(self.REQUIRED):
                # True if we include everything, or value is flagged as required; false otherwise
                if value_type == self.LIST_TYPE:
                    # TODO We could add another list type (or modify the current one) to include
                    # scalar/list/dictionary entries and parse them recursively.
                    # But this is not needed for now, so a list is a simple collection of constants.
                    parsed[key] = {
                        self.TYPE_RESERVED: self.LIST_TYPE,
                        self.CONTENTS: value.get(self.CONTENTS)
                    }
                else:
                    leaf_keys.append(key)
        parsed[self.LEAF] = leaf_keys
        return parsed

    def _validate_type(self, value_type):
        if value_type == None:
            msg = "No type string specified for key %s" % key
            self.logger.error(msg)
            raise JanusSchemaError(msg)
        elif not value_type in self.PERMITTED_TYPES:
            msg = "Illegal type string {}".format(value_type)
            self.logger.error(msg)
            raise JanusSchemaError(msg)
    
    def has_head(self):
        if self.head==None or self.head=={}:
            return False
        else:
            return True

    def validate_table(self, table, input_name=None):
        """validate a Pandas dataframe against the schema"""
        if not input_name:
            input_name = self.UNKNOWN_FILE
        valid = True
        table_column_names = list(table.columns.values)
        if table_column_names != self.body:
            msg = "Input columns [%s] do not match schema columns [%s] in %s" % (
                ', '.join(table_column_names),
                ', '.join(self.body),
                input_name
            )
            self.logger.warning(msg)
            valid = False
        if valid:
            self.logger.info("Table body in %s complies with schema" % input_name)
        else:
            self.logger.warning("Table body in %s DOES NOT comply with schema" % input_name)
        return valid
            
    def validate_meta(self, meta, input_name=None):
        """Validate the metadata header against the schema."""
        if not input_name:
            input_name = self.UNKNOWN_FILE
        if self.has_head():
            required_valid = self._check_required_keys(meta,
                                                       self.required_head_keys,
                                                       input_name,
                                                       self.HEAD)
            permitted_valid = self._check_permitted_keys(meta,
                                                         self.permitted_head_keys,
                                                         input_name,
                                                         self.HEAD)
            valid = required_valid and permitted_valid
        else:
            msg = "No header specified in schema; omitting requested metadata check "+\
                  "on '%s'"% input_name
            self.logger.warning(msg)
            valid = True
        if valid:
            self.logger.info("Metadata header in %s complies with schema" % input_name)
        else:
            self.logger.warning("Metadata header in %s DOES NOT comply with schema" % input_name)
        return valid

    # TODO have a 'path' datatype, and check paths in the config for readability
    #def validate_meta_paths(self, meta):
    #    pass

    def write_template(self, out_file, describe=False):
        """write a template based on the schema"""
        yaml_delimiter = '---'
        print(yaml_delimiter, file=out_file)
        header = self._generate_header_template(self.head, describe=describe)
        # dump header to YAML and convert to list of (non-empty) strings
        header_lines = [x for x in re.split('\n', yaml.dump(header)) if x!='']
        for line in header_lines:
            print('#'+line, file=out_file)
        print(yaml_delimiter, file=out_file)
        print('\t'.join(self.body), file=out_file)
        print('\t'.join([x.lower()+'_value' for x in self.body]), file=out_file)


class JanusSchemaError(Exception):
    pass
