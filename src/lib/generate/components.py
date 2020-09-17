"""Classes to represent components of a cBioPortal study

Eg. study metadata, clinical sample/patient data, pipeline outputs
"""

import logging
import os
import pandas as pd
import re
import yaml


from utilities.base import base
import utilities.constants
from utilities.config import legacy_config_wrapper
from generate.config import cancer_type_config, case_list_config, clinical_config, pipeline_config

class component(base):

    """
    Base class for data/metadata components of a cBioPortal study
    Eg. Study metadata, clinical sample/patient data, pipeline output
    Subclasses can call super().__init__() to set up simple logging
    """

    def __init__(self, log_level=logging.WARN):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__))

    def write(self, out_dir):
        self.logger.warning("Placeholder write() method of base class, should not be called")

class dual_output_component(component):

    """
    Base class for components with separate data and metadata files
    """

    def write_data(self, out_dir):
        self.logger.warning("Placeholder write_data() method of base class, should not be called")

    def write_meta(self, out_dir):
        self.logger.warning("Placeholder write_meta() method of base class, should not be called")

    def write(self, out_dir):
        self.write_data(out_dir)
        self.write_meta(out_dir)

class alteration_type(component):
    """
    Class to represent a cBioPortal alteration type; contains one or more pipeline components
    """

    def __init__(self, alteration_type_name, config_paths_by_datatype, study_config,
                 log_level=logging.WARN):
        super().__init__(log_level)
        self.name = alteration_type_name
        self.components = []
        if len(config_paths_by_datatype)==0:
            self.logger.warning("No datatypes provided to alteration type '%s'" % alteration_type_name)
        factory = pipeline_component_factory(log_level)
        for key in config_paths_by_datatype.keys():
            pc = factory.get_component(self.name, key, config_paths_by_datatype[key], study_config)
            if pc == None:
                msg = "No component found for alteration type '%s', " % self.name +\
                      "config path '%s'" % config_paths_by_datatype[key]
                self.logger.error(msg)
                raise JanusComponentError(msg)
            self.components.append(pc)
        self.logger.debug("Created %i components for %s" % (len(self.components), self.name))

    def consensus_meta_value(self, key):
        """
        Get the value of a metadata field; check if consistent between all subcomponents.
        Return the first non-null value found (if any), None otherwise.
        """
        consensus = None
        for component in self.components:
            value = component.get_meta_value(key)
            if value == None:
                msg = "Metadata value for %s not found in component %s" % key, component.name
                self.logger.warning(msg)
            elif consensus == None:
                consensus = value
            elif value != consensus:
                msg = "Inconsistent metadata value for %s in component %s" % key, component.name
                self.logger.warn(msg)
        return consensus

    def get_profile_description(self):
        """Get the profile_description field, if consistent between subcomponents"""
        return self.consensus_meta_value("profile_description")

    def get_profile_name(self):
        """Get the profile_name field, if consistent between subcomponents"""
        return self.consensus_meta_value("profile_name")

    def get_sample_ids(self):
        """Get the SAMPLE_ID column as a list; check if consistent between subcomponents"""
        sample_id_set = None
        samples = []
        consistent = True
        for component in self.components:
            samples = component.get_sample_ids()
            if sample_id_set == None:
                sample_id_set = set(samples)
            elif set(samples) != sample_id_set:
                msg = "Inconsistent SAMPLE_ID values in pipeline component %s" % component.name
                self.logger.warning(msg)
                consistent = False
        if not consistent:
            self.logger.warning("Inconsistent SAMPLE_ID values; returning first non-empty set found")
        elif len(samples) == 0:
            self.logger.warning("No SAMPLE_ID values found for any component in %s") % self.name
        return samples

    def get_name(self):
        return self.name

    def write(self, out_dir):
        for pc in self.pipeline_components:
            pc.write(out_dir)

class cancer_type(dual_output_component):

    """cancer_type component, including dedicated colours and type_of_cancer from study"""

    DATATYPE = utilities.constants.CANCER_TYPE_DATATYPE
    DATA_FILENAME = 'data_cancer_type.txt'
    META_FILENAME = 'meta_cancer_type.txt'
    COLOUR_FILENAME = 'cancer_colours.csv'
    DEFAULT_COLOUR = 'lavender' # default colour for general cancer awareness

    COLOR_KEY = 'dedicated_color'
    DATA_FILENAME_KEY = 'data_filename_key'
    KEYWORDS_KEY = 'clinical_trial_keywords'
    NAME_KEY = 'name'
    PARENT_KEY = 'parent_type_of_cancer'
    TYPE_OF_CANCER_KEY = 'type_of_cancer'

    def __init__(self, config, default_cancer_type_string=None):
        super().__init__()
        # default_cancer_type_string is from study metadata, may be used for "type_of_cancer" field
        self.config = config
        # check config fields are consistent
        self.rows = len(config.get(self.NAME_KEY))
        for key in [self.KEYWORDS_KEY, self.PARENT_KEY, self.COLOR_KEY, self.TYPE_OF_CANCER_KEY]:
            value = config.get(key)
            if key in [self.COLOR_KEY, self.TYPE_OF_CANCER_KEY] and value == None:
                pass # these values may be null
            elif len(config.get(key)) != self.rows:
                msg = "Incorrect number of fields for cancer_type config key %s" % key
                self.logger.error(msg)
                raise ValueError(msg)
        # generate the 'type_of_cancer' column
        if config.get(self.TYPE_OF_CANCER_KEY):
            self.type_of_cancer_column = config.get(self.TYPE_OF_CANCER_KEY)
        else:
            self.type_of_cancer_column = [default_cancer_type_string]*self.rows
        # generate the 'colours' column; attempt to find a matching colour in reference file
        if config.get(self.COLOR_KEY):
            self.colours_column = config.get(self.COLOR_KEY)
        else:
            # read colours reference as a pandas dataframe
            ref_path = os.path.join(
                os.path.dirname(__file__),
                utilities.constants.DATA_DIRNAME,
                self.COLOUR_FILENAME
            )
            colours = pd.read_csv(ref_path))
            self.colours_column = []
            for name in config.get(self.NAME_KEY):
                # use .casefold() instead of .lower() to handle special cases
                name_expr = re.compile(name.casefold())
                candidate_colours = []
                for index, row in colours.iterrows():
                    ref_name = row[self.CONFIG_NAME_KEY]
                    if name_expr.search(ref_name.casefold()):
                        candidate_colours.append(row['COLOUR'])
                distinct_colour_total = len(set(candidate_colours))
                if distinct_colour_total == 0:
                    colour = self.DEFAULT_COLOUR_NAME
                elif distinct_colour_total == 1:
                    colour = candidate_colours[0].casefold()
                else:
                    colour = self.DEFAULT_COLOUR_NAME
                    msg = "Conflicting colour values found for cancer name "+\
                          "'%s', defaulting to '%s'" % (name, colour)
                    self.logger.warning(msg)
                self.colours_column.append(colour)

    def write_data(self, out_dir):
        out = open(os.path.join(out_dir, self.DATA_FILENAME), 'w')
        for i in range(self.rows):
            values = [
                self.type_of_cancer_column[i],
                self.config.get(self.NAME_KEY)[i],
                self.config.get(self.KEYWORDS_KEY)[i],
                self.colours_column[i],
                self.config.get(self.PARENT_KEY)[i],
            ]
            print("\t".join(values), file=out)
        out.close()

    def write_meta(self, out_dir):
        meta = {}
        meta['genetic_alteration_type'] = self.DATATYPE
        meta['datatype'] = self.DATATYPE
        meta['data_filename'] = self.DATA_FILENAME
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()

class case_list(component):

    CATEGORY_KEY = 'category'
    NAME_KEY = 'case_list_name'
    DESC_KEY = 'case_list_description'

    def __init__(self, study_id, suffix, name, description, samples, category=None,
                 log_level=logging.WARN):
        super().__init__(log_level)
        self.cancer_study_identifier = study_id
        self.suffix = suffix
        self.stable_id = "%s_%s" % (study_id, suffix)
        self.case_list_name = name
        self.case_list_description = description
        self.samples = samples
        self.category = category

    @classmethod
    def from_config_path(klass, path, study_id):
        # Creates & returns a new instance of case_list, with parameters read from path
        config = case_list_config(path)
        meta = config.get_meta()
        if klass.CATEGORY_KEY in meta:
            category = meta[klass.CATEGORY_KEY]
        else:
            category = None
        return klass(
            study_id,
            meta['suffix'],
            meta[klass.NAME_KEY],
            meta[klass.DESC_KEY],
            config.get_sample_ids(),
            category
        )

    def write(self, out_dir):
        data = {}
        data['cancer_study_identifier'] = self.cancer_study_identifier
        data['stable_id'] = self.stable_id
        data[self.NAME_KEY] = self.case_list_name
        data[self.DESC_KEY] = self.case_list_description
        data['case_list_ids'] = "\t".join(self.samples)
        if self.category != None:
            data[self.CATEGORY_KEY] = self.category
        out_path = os.path.join(out_dir, 'cases_%s.txt' % self.suffix)
        if os.path.exists(out_path):
            msg = "Output path already exists; not overwriting; case list suffix %s may not be unique" \
                  % self.suffix
            self.logger.warn(msg)
        out = open(out_path, 'w')
        for key in data.keys():
            # not using YAML dump; we want a literal tab-delimited string, not YAML representation
            print("%s: %s" % (key, data[key]), file=out)
        out.close()
    
        
class clinical_data_component(dual_output_component):

    """Clinical patient/sample data in a cBioPortal study"""

    DATATYPE = '_placeholder_'
    DATA_FILENAME = '_data_placeholder_'
    META_FILENAME = '_meta_placeholder_'
    DEFAULT_PRECISION = 3
    
    ATTRIBUTE_NAMES_KEY = 'attribute_names'
    DATATYPES_KEY = 'datatypes'
    DESCRIPTIONS_KEY = 'descriptions'
    DISPLAY_NAMES_KEY = 'display_names'
    PRIORITIES_KEY = 'priorities'
    PRECISION_KEY = 'precision'

    def __init__(self, samples, samples_meta, study_id, log_level=logging.WARN):
        super().__init__(log_level)
        self.cancer_study_identifier = study_id
        self.samples = samples
        self.samples_meta = samples_meta
        self.precision = self.sample_meta.get(self.PRECISION_KEY, self.DEFAULT_PRECISION)

    def write_data(self, out_dir):
        """Write header; then write selected attributes of samples"""
        out = open(os.path.join(out_dir, self.DATA_FILENAME), 'w')
        attribute_names = self.samples_meta[self.ATTRIBUTE_NAMES_KEY]
        self.logger.debug("Writing data file header for %s" % self.DATATYPE)
        print("#"+"\t".join(self.samples_meta[self.DISPLAY_NAMES_KEY]), file=out)
        print("#"+"\t".join(self.samples_meta[self.DESCRIPTIONS_KEY]), file=out)
        print("#"+"\t".join(self.samples_meta[self.DATATYPES_KEY]), file=out)
        print("#"+"\t".join(self.samples_meta[self.PRIORITIES_KEY]), file=out)
        print("#"+"\t".join(attribute_names), file=out)
        self.logger.debug("Writing data file table for %s" % self.DATATYPE)
        for sample in self.samples:
            fields = []
            for name in attribute_names:
                value = sample.get(name)
                if value == None:
                    field = 'NULL' # interpreted as NaN by pandas
                elif isinstance(value, float):
                    format_str = "%.{}f".format(self.precision)
                    field = format_str % value
                else:
                    field = str(value)
                fields.append(field)
            print("\t".join(fields), file=out)
        out.close()

    def write_meta(self, out_dir):
        meta = {}
        meta['cancer_study_identifier'] = self.cancer_study_identifier
        meta['genetic_alteration_type'] = 'CLINICAL'
        meta['datatype'] = self.DATATYPE
        meta['data_filename'] = self.DATA_FILENAME
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()

class patients_component(clinical_data_component):

    DATATYPE = utilities.constants.PATIENT_DATATYPE
    DATA_FILENAME = 'data_clinical_patients.txt'
    META_FILENAME = 'meta_clinical_patients.txt'

class samples_component(clinical_data_component):

    DATATYPE = utilities.constants.SAMPLE_DATATYPE
    DATA_FILENAME = 'data_clinical_samples.txt'
    META_FILENAME = 'meta_clinical_samples.txt'


class pipeline_component_factory(base):

    """Construct pipeline components for a given ALTERATIONTYPE and DATATYPE"""

    CLASSNAMES = {
        ('COPY_NUMBER_ALTERATION', 'CAP_CNA'): 'legacy_pipeline_component',
        ('COPY_NUMBER_ALTERATION', 'Sequenza'): 'legacy_pipeline_component',
        ('MRNA_EXPRESSION', 'CAP_expression'): 'legacy_pipeline_component',
        ('MRNA_EXPRESSION', 'Cufflinks'): 'legacy_pipeline_component',
        ('MUTATION_EXTENDED', 'CAP_mutation'): 'legacy_pipeline_component',
        ('MUTATION_EXTENDED', 'Mutect'): 'legacy_pipeline_component',
        ('MUTATION_EXTENDED', 'Mutect2'): 'legacy_pipeline_component',
        ('MUTATION_EXTENDED', 'MutectStrelka'): 'legacy_pipeline_component',
        ('MUTATION_EXTENDED', 'Strelka'): 'legacy_pipeline_component'
    }

    # factory to supply appropriate pipeline component class, given name strings
    # see https://stackoverflow.com/questions/51142320/how-to-instantiate-class-by-its-string-name-in-python-from-current-file

    def __init__(self, log_level=logging.WARN):
        self.log_level = log_level
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__))

    def get_component(self, alt_type, datatype, config_path, study_config):
        # some legacy components need the global study config
        # TODO factor out this requirement; create with the component config plus specific variables
        # TODO we are reading the pipeline config twice (here and in component_class); avoid?
        # TODO clarify the distinction between cBioPortal 'datatype name' and Janus 'pipeline name'
        config = pipeline_config(config_path)
        pipeline_name = config.get_meta_value('pipeline')
        if pipeline_name == None:
            self.logger.debug("No pipeline configured, using datatype %s" % datatype)
            pipeline_name = datatype # for CAP_expression test
        classname = self.CLASSNAMES.get((alt_type, pipeline_name), None)
        if classname == None:
            self.logger.warning("No classname found for (%s, %s)" % (alt_type, pipeline_name))
            return None
        component_class = globals()[classname]
        return component_class(alt_type, pipeline_name, config_path, study_config, self.log_level)


class pipeline_component(component):

    """Basic unit of pipeline output; results for a given alteration_type and data_type"""

    def __init__(self, alterationtype_name, datatype_name, config_path, study_config,
                 log_level=logging.WARN):
        super().__init__(log_level)
        self.atype = alterationtype_name
        self.dtype = datatype_name
        self.name = "%s:%s" % (self.atype, self.dtype)
        self.config = pipeline_config(config_path)
        self.study_config = study_config
        self.logger.debug("Created data handler for '%s' from path %s" % (self.name, config_path))

    def get_meta_value(self, key):
        """Return self.meta[key] if present, None otherwise"""
        return self.config.get_meta().get(key, None)

    def get_sample_ids(self):
        """Return the SAMPLE_ID column, if any, as a list"""
        dataframe = self.config.get_table()
        key = 'SAMPLE_ID'
        samples = []
        if key in dataframe.columns:
            samples = dataframe[key].tolist()
        else:
            self.logger.warning("No sample IDs found for pipeline component %s" % self.name)
        return samples

    def write(self, out_dir, dry_run=False):
        # TODO use this method for new (non-legacy) pipeline output types
        self.logger.warning("Output for pipeline component '%s' not yet supported" % self.name)
        if dry_run:
            self.logger.info("Dry run for unsupported pipeline component %s" % self.name)
        else:
            msg = "Pipeline component '%s' is not supported for execution" % self.name
            self.logger.error(msg)
            raise ValueError(msg)


class legacy_pipeline_component(pipeline_component):

    """Run a legacy datahandler script using exec"""

    def __init__(self, atype_name, dtype_name, config_path, study_config, log_level=logging.WARN):
        super().__init__(atype_name, dtype_name, config_path, study_config, log_level)
        self.legacy_config = legacy_config_wrapper(self.config, atype_name, dtype_name)
        self.legacy_config_study = legacy_config_wrapper(self.study_config, atype_name, dtype_name)

    def write(self, out_dir, dry_run=False):
        # legacy method; construct path to a script and run using exec()
        # !!! DEPRECATED WITH EXTREME PREJUDICE !!!
        # TODO refactor to remove legacy elements
        module_dir = os.path.dirname((os.path.abspath(__file__)))
        # root dir of janus source; may be required for some legacy scripts
        janus_path = os.path.abspath(os.path.join(module_dir, os.pardir, os.pardir, os.pardir))
        script_path = os.path.join(module_dir, 'analysis_pipelines', self.atype, "%s.py" % self.dtype)
        # workaround; legacy code sets output directory in the study config object
        self.legacy_config_study.set_config_mapping('output_folder', out_dir)
        global_args = {
            'meta_config': self.legacy_config,
            'study_config': self.legacy_config_study,
            'janus_path': janus_path,
            'logger': self.logger,
            "__name__": "__main__"
        }
        local_args = {}
        if not (os.path.exists(script_path) and os.access(script_path, os.R_OK)):
            msg = "Legacy pipeline script path %s does not exist, or is not readable" % script_path
            self.logger.error(msg)
            raise(OSError(msg))
        with open(script_path, 'rb') as script_file:
            try:
                compiled = compile(script_file.read(), script_path, 'exec')
                self.logger.debug("Legacy pipeline script %s compiled successfully" % script_path)
            except Exception as exc:
                msg = "Legacy pipeline script %s does not compile: %s" % (script_path, str(exc))
                self.logger.error(msg)
                raise
        if dry_run:
            msg = "%s: Dry run of script %s, global_args %s" % (self.name, script_path, str(global_args))
            self.logger.info(msg)
        else:
            self.logger.debug("%s: Running legacy pipeline script %s" % (self.name, script_path))
            try:
                exec(compiled, globals().update(global_args), local_args)
            except Exception as exc:
                self.logger.error("Unexpected error in legacy pipeline exec: "+str(exc))
                raise


class study_meta(component):

    """Metadata for the study; no data in this component"""

    META_FILENAME = 'meta_study.txt'

    def __init__(self, study_meta, log_level=logging.WARN):
        super().__init__(log_level)
        self.study_meta = study_meta

    def get(self, key):
        return self.study_meta.get(key)

    def write(self, out_dir):
        meta = {}
        for field in utilities.constants.REQUIRED_STUDY_META_FIELDS:
            try:
                meta[field] = self.study_meta[field]
            except KeyError:
                msg = "Missing required study meta field "+field
                self.logger.error(msg)
                raise
        for field in utilities.constants.OPTIONAL_STUDY_META_FIELDS:
            if self.study_meta.get(field):
                meta[field] = self.study_meta[field]
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()

class JanusComponentError(Exception):
    pass
