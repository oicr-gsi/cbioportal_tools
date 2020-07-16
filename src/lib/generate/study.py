"""Class to represent a study directory, formatted for upload to cBioPortal"""

import os
import sys
import yaml

from utilities.config import config
from utilities.constants import REQUIRED_STUDY_META_FIELDS, OPTIONAL_STUDY_META_FIELDS

class study:

    def __init__(self, config_path):
        config = study_config(config_path)
        self.study_meta = self.get_study_meta(config) # required
        self.clinical_data = self.get_clinical_data(config) # sample data is required
        self.cancer_type = self.get_cancer_type(config)
        self.case_list = self.get_case_list(config)
        self.pipelines = self.get_pipelines(config) # warn if empty

    def get_study_meta(self, config):
        return study_meta(config)

    def get_clinical_data(self, config):
        samples = clinical_samples(config)
        return [samples, None]
    
    def get_cancer_type(self, config):
        return None
    
    def get_case_list(self, config):
        return None

    def get_pipelines(self, config):
        return []
        
    def write_all(self, out_dir):
        """Write all outputs to the given directory path"""
        # validate the output directory
        if not os.path.exists(out_dir):
            raise OSError("Output directory %s does not exist" % out_dir)
        elif not os.path.isdir(out_dir):
            raise OSError("Output path %s is not a directory" % out_dir)
        elif not os.access(out_dir, os.W_OK):
            raise OSError("Output path %s is not writable" % out_dir)
        # write component files
        for component in [self.study_meta, self.cancer_type, self.case_list]:
            if component != None:
                component.write_all(out_dir)
        for component in self.clinical_data:
            if component != None:
                component.write_all(out_dir)
        for pipeline in self.pipelines:
            for datahandler in pipeline.datahandlers:
                datahandler.write_all(out_dir)


class study_config(config):
    """cBioPortal study config in Janus format"""
    pass

                
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
        self.filename = config.get_sample_filename()
        print(self.filename)

    def write_all(self, out_dir):
        print("### Placeholder: Sample output to "+out_dir)
