"""Classes to represent components of a cBioPortal study

Eg. study metadata, clinical sample/patient data, pipeline outputs
"""

import os
import sys
import yaml

from utilities.config import config
import utilities.constants
from generate.config import cancer_type_config, clinical_config

class study_component:

    """
    Base class for data/metadata components of a cBioPortal study
    Eg. Study metadata, clinical sample/patient data, pipeline output
    """

    DATA_FILENAME = '_data_placeholder_'
    META_FILENAME = '_meta_placeholder_'
    
    def __init__(self, config):
        self.config = config

    def write_data(self, out_dir):
        # TODO use logger instead
        print("Warning: Placeholder method of base class, should not be called", file=sys.stderr)

    def write_meta(self, out_dir):
        # TODO use logger instead
        print("Warning: Placeholder method of base class, should not be called", file=sys.stderr)

    def write_all(self, out_dir):
        self.write_data(out_dir)
        self.write_meta(out_dir)
        

class cancer_type(study_component):

    DATATYPE = utilities.constants.CANCER_TYPE_DATATYPE
    DATA_FILENAME = 'data_cancer_type.txt'
    META_FILENAME = 'meta_cancer_type.txt'

    def __init__(self, cancer_type_config_path):
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

class case_list(study_component):

    def __init__(self, study_id, suffix, name, description, samples, category=None):
        self.cancer_study_identifier = study_id
        self.stable_id = "%s_%s" % (study_id, suffix)
        self.case_list_name = name
        self.case_list_description = description
        self.samples = samples
        self.category = category

    @classmethod
    def from_config_path(klass, path):
        # TODO create & return a new instance of klass with data read from path
        # ie. klass(study_id, suffix, name, description, samples, category)
        pass

    def write_all(self, out_dir, filename):
        data = {}
        data['cancer_study_identifier'] = self.cancer_study_identifier
        data['stable_id'] = self.stable_id
        data['case_list_name'] = self.case_list_name
        data['case_list_description'] = self.case_list_description
        data['case_list_ids'] = "\t".join(self.samples)
        if self.category != None:
            data['category'] = self.category
        out = open(os.path.join(out_dir, filename), 'w')
        out.write(yaml.dump(meta))
        out.close()
    
        
class clinical_data_component(study_component):

    """Clinical patient/sample data in a cBioPortal study"""

    DATATYPE = '_placeholder_'

    def __init__(self, clinical_config_path, study_id):
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


class study_meta(study_component):

    """Metadata for the study; no data in this component"""

    META_FILENAME = 'meta_study.txt'

    def __init__(self, study_config):
        self.study_meta = study_config.get_meta()
    
    def write_all(self, out_dir):
        meta = {}
        for field in utilities.constants.REQUIRED_STUDY_META_FIELDS:
            try:
                meta[field] = self.study_meta[field]
            except KeyError:
                msg = "Missing required study meta field "+field
                print(msg, file=sys.stderr) # TODO add logger
        for field in utilities.constants.OPTIONAL_STUDY_META_FIELDS:
            if field in self.study_meta:
                meta[field] = self.study_meta[field]
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()
