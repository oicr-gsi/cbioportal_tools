"""Class to represent a study directory, formatted for upload to cBioPortal"""

import os

from generate.components import study_meta, patients, samples
from generate.config import study_config

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
        return [samples(config), patients(config)]
    
    def get_cancer_type(self, config):
        return None
    
    def get_case_list(self, config):
        return None

    def get_pipelines(self, config):
        return []

    def is_valid_output_dir(self, out_dir):
        """validate an output directory"""
        # TODO use a logger instead of immediately raising error
        valid = True
        if not os.path.exists(out_dir):
            valid = False
            raise OSError("Output directory %s does not exist" % out_dir)
        elif not os.path.isdir(out_dir):
            valid = False
            raise OSError("Output path %s is not a directory" % out_dir)
        elif not os.access(out_dir, os.W_OK):
            valid = False
            raise OSError("Output path %s is not writable" % out_dir)
        return valid

    def write_all(self, out_dir):
        """Write all outputs to the given directory path"""
        # write component files
        self.is_valid_output_dir(out_dir)
        for component in [self.study_meta, self.cancer_type, self.case_list]:
            if component != None:
                component.write_all(out_dir)
        for component in self.clinical_data:
            if component != None:
                component.write_all(out_dir)
        for pipeline in self.pipelines:
            for datahandler in pipeline.datahandlers:
                datahandler.write_all(out_dir)

