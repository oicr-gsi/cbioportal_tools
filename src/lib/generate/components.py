"""Classes to represent components of a cBioPortal study

Eg. study metadata, clinical sample/patient data, pipeline outputs
"""

import os
import yaml

from utilities.config import config
from utilities.constants import REQUIRED_STUDY_META_FIELDS, OPTIONAL_STUDY_META_FIELDS
from generate.config import clinical_config

class study_component:

    """
    Base class for data/metadata components of a cBioPortal study
    Eg. Study metadata, clinical sample/patient data, pipeline output
    """

    DATA_FILENAME = '_data_placeholder_'
    META_FILENAME = '_meta_placeholder_'
    
    def __init__(self, config):
        self.config = config

    def write_all(self, out_dir):
        pass
        

class study_meta(study_component):

    """Metadata for the study; no data in this component"""

    META_FILENAME = 'meta_study.txt'
    
    def __init__(self, config):
        self.study_meta = config.meta
        
    def write_all(self, out_dir):
        meta = {}
        for field in REQUIRED_STUDY_META_FIELDS:
            try:
                meta[field] = self.study_meta[field]
            except KeyError:
                msg = "Missing required study meta field "+field
                print(msg, file=sys.stderr) # TODO add logger
        for field in OPTIONAL_STUDY_META_FIELDS:
            if field in self.study_meta:
                meta[field] = self.study_meta[field]
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()

class clinical_samples(study_component):

    DATA_FILENAME = 'data_clinical_samples.txt'
    META_FILENAME = 'meta_clinical_samples.txt'

    def __init__(self, config):
        self.cancer_study_identifier = config.get_cancer_study_identifier()
        sample_config_path = config.get_sample_config_path()
        self.sample_config = clinical_config(sample_config_path)

    def write_data(self, out_dir):
        out = open(os.path.join(out_dir, self.DATA_FILENAME), 'w')
        for row in self.sample_config.get_clinical_headers():
            print('#'+'\t'.join(row), file=out)
        print(self.sample_config.data_as_tsv(), file=out)
        out.close()

    def write_meta(self, out_dir):
        meta = {}
        meta['cancer_study_identifier'] = self.cancer_study_identifier
        meta['genetic_alteration_type'] = 'CLINICAL'
        meta['datatype'] = 'SAMPLE_ATTRIBUTES'
        meta['data_filename'] = self.DATA_FILENAME
        out = open(os.path.join(out_dir, self.META_FILENAME), 'w')
        out.write(yaml.dump(meta, sort_keys=True))
        out.close()
        
    def write_all(self, out_dir):
        self.write_data(out_dir)
        self.write_meta(out_dir)
