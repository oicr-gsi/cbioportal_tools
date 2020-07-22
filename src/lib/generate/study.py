"""Class to represent a study directory, formatted for upload to cBioPortal"""

import logging
import os

from generate.components import alteration_type, cancer_type, case_list, study_meta, patients, samples
from generate.config import study_config
from utilities.base import base
import utilities.constants

class study(base):

    def __init__(self, config_path, log_level=logging.WARNING):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__))
        config = study_config(config_path, log_level)
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
            msg = "Clinical sample data is required, but has not been configured"
            self.logger.error(msg)
            raise ValueError(msg)
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

        # generate custom case lists from config files
        case_list_config_paths = config.get_case_list_config_paths()
        case_lists = []
        for path in case_list_config_paths:
            case_lists.append(case_list.from_config_path(path, self.study_id))
        return case_lists

    def get_pipelines(self, config):
        config_paths = config.get_alterationtype_config_paths()
        alteration_types = []
        log_level = self.logger.getEffectiveLevel()
        for name in config_paths.keys():
            self.logger.debug("Found alteration type %s" % name)
            alteration_types.append(alteration_type(name, config_paths[name], log_level))
        return alteration_types

    def is_valid_output_dir(self, out_dir):
        """validate an output directory"""
        valid = True
        if not os.path.exists(out_dir):
            valid = False
            self.logger.error("Output directory %s does not exist" % out_dir)
        elif not os.path.isdir(out_dir):
            valid = False
            self.logger.error("Output path %s is not a directory" % out_dir)
        elif not os.access(out_dir, os.W_OK):
            valid = False
            self.logger.error("Output path %s is not writable" % out_dir)
        return valid

    def write_all(self, out_dir):
        """Write all outputs to the given directory path"""
        # write component files
        valid = self.is_valid_output_dir(out_dir)
        if not valid:
            msg = "Invalid output directory %s; exiting" % out_dir
            self.logger.error(msg)
            raise OSError(msg)
        case_list_dir = os.path.join(out_dir, 'case_lists')
        if len(self.case_lists) > 0:
            if os.path.exists(case_list_dir):
                self.is_valid_output_dir(case_list_dir)
            else:
                os.makedirs(case_list_dir)
        for component in [self.study_meta, self.cancer_type]:
            if component != None:
                component.write(out_dir)
        for case_list in self.case_lists:
            case_list.write(case_list_dir)
        for clinical_component in self.clinical_data:
            if clinical_component != None:
                clinical_component.write(out_dir)
        for pipeline in self.pipelines:
            self.logger.debug("Found pipeline: "+str(pipeline.name))
            self.logger.debug("Found %i datahandlers" % len(pipeline.datahandlers))
            for datahandler in pipeline.datahandlers:
                self.logger.debug("Writing output for datahandler '%s'" % datahandler.name)
                datahandler.write(out_dir)

