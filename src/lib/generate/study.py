"""Class to represent a study directory, formatted for upload to cBioPortal"""

import os

from generate.components import cancer_type, study_meta, patients, samples
from generate.config import study_config
import utilities.constants

class study:

    def __init__(self, config_path):
        config = study_config(config_path)
        self.study_id = config.get_cancer_study_identifier()
        self.study_meta = self.get_study_meta(config) # required
        self.clinical_data = self.get_clinical_data(config) # sample data is required
        self.cancer_type = self.get_cancer_type(config)
        self.pipelines = self.get_pipelines(config) # warn if empty
        self.case_lists = self.get_case_lists(config)

    def get_study_meta(self, config):
        return study_meta(config)

    def get_clinical_data(self, config):
        # read sample data
        sample_config_path = config.get_sample_config_path()
        if sample_config_path == None:
            raise ValueError("Clinical sample data is required, but has not been configured")
        sample_component = samples(sample_config_path, self.study_id)
        # read optional patient data
        patient_config_path = config.get_patient_config_path()
        if patient_config_path == None:
            patient_component = None
        else:
            patient_component = patients(patient_config_path, self.study_id)
        return [sample_component, patient_component]
    
    def get_cancer_type(self, config):
        return cancer_type(config.get_cancer_type_config_path())

    def get_case_lists(self, config):
        # TODO:
        # - generate case lists for pipelines which require them (use self.pipelines)
        # - read and generate case lists from custom config
        # - use self.study_id for case_list construction
        return []

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
        case_list_dir = os.path.join(out_dir, 'case_lists')
        if len(self.case_lists) > 0:
            if os.path.exists(case_list_dir):
                self.is_valid_output_dir(case_list_dir)
            else:
                os.makedirs(case_list_dir)
        for component in [self.study_meta, self.cancer_type]:
            if component != None:
                component.write_all(out_dir)
        for case_list in self.case_lists:
            case_list.write_all(case_list_dir)
        for clinical_component in self.clinical_data:
            if clinical_component != None:
                clinical_component.write_all(out_dir)
        for pipeline in self.pipelines:
            for datahandler in pipeline.datahandlers:
                datahandler.write_all(out_dir)

