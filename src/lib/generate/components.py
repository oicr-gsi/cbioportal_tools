"""Classes to represent components of a cBioPortal study

Eg. study metadata, clinical sample/patient data, pipeline outputs
"""

import logging
import os
import yaml

from utilities.base import base
import utilities.constants
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

    def __init__(self, alteration_type_name, config_paths_by_datatype, log_level=logging.WARN):
        super().__init__(log_level)
        self.name = alteration_type_name
        self.components = []
        if len(config_paths_by_datatype)==0:
            self.logger.warning("No datatypes provided to alteration type '%s'" % alteration_type_name)
        for key in config_paths_by_datatype.keys():
            pc = pipeline_component(self.name, key, config_paths_by_datatype[key], log_level)
            self.components.append(pc)
        self.logger.debug("Created %i components for %s" % (len(self.components), self.name))

    def write(self, out_dir):
        for pc in self.pipeline_components:
            pc.write(out_dir)

class cancer_type(dual_output_component):

    DATATYPE = utilities.constants.CANCER_TYPE_DATATYPE
    DATA_FILENAME = 'data_cancer_type.txt'
    META_FILENAME = 'meta_cancer_type.txt'

    def __init__(self, cancer_type_config_path):
        super().__init__()
        self.config = cancer_type_config(cancer_type_config_path)

    def write_data(self, out_dir):
        out = open(os.path.join(out_dir, self.DATA_FILENAME), 'w')
        print(self.config.data_as_tsv(), end='', file=out)
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
            msg = "Output path already exists; non-unique case list suffix?"
            self.logger.error(msg)
            raise OSError(msg)
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

    def __init__(self, clinical_config_path, study_id, log_level=logging.WARN):
        super().__init__(log_level)
        self.cancer_study_identifier = study_id
        self.config = clinical_config(clinical_config_path)

    def write_data(self, out_dir):
        out = open(os.path.join(out_dir, self.DATA_FILENAME), 'w')
        for row in self.config.get_clinical_headers():
            print('#'+'\t'.join(row), file=out)
        print(self.config.data_as_tsv(), end='', file=out)
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

class patients(clinical_data_component):

    DATATYPE = utilities.constants.PATIENT_DATATYPE
    DATA_FILENAME = 'data_clinical_patients.txt'
    META_FILENAME = 'meta_clinical_patients.txt'

class samples(clinical_data_component):

    DATATYPE = utilities.constants.SAMPLE_DATATYPE
    DATA_FILENAME = 'data_clinical_samples.txt'
    META_FILENAME = 'meta_clinical_samples.txt'


class pipeline_component(component):

    """Basic unit of pipeline output; results for a given alteration_type and data_type"""

    def __init__(self, alterationtype_name, datatype_name, config_path, log_level=logging.WARN):
        super().__init__(log_level)
        self.atype = alterationtype_name
        self.dtype = datatype_name
        self.name = "%s:%s" % (self.atype, self.dtype)
        self.config = pipeline_config(config_path)
        self.logger.debug("Created data handler for '%s' from path %s" % (self.name, config_path))

    # TODO write data for appropriate datahandler
    # old method is to generate a path to a python script and run using exec :-(
    # new way: create an instance of appropriate class and call its write method
    # for now, the "new class" may simply be a wrapper for the old method

    # TODO make a data handler module with a factory to supply appropriate datahandler class
    # see https://stackoverflow.com/questions/51142320/how-to-instantiate-class-by-its-string-name-in-python-from-current-file
    # eg. self.handler = self.get_handler(self.atype, self.dtype) where get_handler calls the factory

    # TODO may be more natural to have alteration_type as the container for handler objects

    def write(self, out_dir):
        # TODO self.handler.write(outdir)
        self.logger.error("Output for pipeline component '%s' not yet enabled" % self.name)

class legacy_pipeline_component(pipeline_component):

    """Run a legacy datahandler script using exec"""

    pass

class pipeline_component_factory(base):

    """Construct pipeline components for a given ALTERATIONTYPE and DATATYPE"""

    def __init__(self, log_level=logging.WARN):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__))

    def get_component(self, alt_type, datatype):
        pass


class study_meta(component):

    """Metadata for the study; no data in this component"""

    META_FILENAME = 'meta_study.txt'

    def __init__(self, study_config, log_level=logging.WARN):
        super().__init__(log_level)
        self.study_meta = study_config.get_meta()
    
    def write(self, out_dir):
        meta = {}
        # TODO check all required fields are present
        for field in utilities.constants.REQUIRED_STUDY_META_FIELDS:
            try:
                meta[field] = self.study_meta[field]
            except KeyError:
                msg = "Missing required study meta field "+field
                self.logger.error(msg)
        for field in utilities.constants.OPTIONAL_STUDY_META_FIELDS:
            if field in self.study_meta:
                meta[field] = self.study_meta[field]
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()
