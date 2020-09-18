"""Class to represent a study directory, formatted for upload to cBioPortal"""

import json
import logging
import os
from shutil import rmtree


from generate.components import alteration_type, cancer_type, case_list, study_meta, \
    patients_component, samples_component

from generate.config import study_config

from generate.sample import sample

from utilities.base import base
import utilities.constants

class study(base):

    CANCER_TYPE_KEY = 'cancer_type'
    CASE_LISTS_KEY = 'case_lists'
    GENETIC_ALTERATIONS_KEY = 'genetic_alterations'
    SAMPLES_KEY = 'samples'
    SAMPLES_META_KEY = 'samples_meta'
    STUDY_ID_KEY = 'cancer_study_identifier'
    STUDY_META_KEY = 'study_meta'
    TYPE_OF_CANCER_KEY = 'type_of_cancer'
    WRITE_PATIENTS_KEY = 'write_patients'

    # 'cancer type' and 'type of cancer' are distinct terms in cBioPortal
    # respectively, they are an output file format, and a string in study metadata
    
    def __init__(self, config_path, log_level=logging.WARNING, log_path=None):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__), log_path)
        with open(config_path, 'r') as config_file:
            config = json.loads(config_file.read())
        # TODO validate the config JSON
        study_meta_config = config.get(self.STUDY_META_KEY)
        self.study_id = study_meta_config.get(self.STUDY_ID_KEY)
        type_of_cancer_string = study_meta_config.get(self.TYPE_OF_CANCER_KEY)
        self.cancer_type = cancer_type(config.get(self.CANCER_TYPE_KEY), type_of_cancer_string)
        self.study_meta = study_meta(study_meta_config)
        
        # TODO update case list handling
        self.case_list_config = config.get(self.CASE_LISTS_KEY)                                       

        # read sample info; cross-reference with attribute meta to get clinical data components
        self.samples = []
        for sample_json in config.get(self.SAMPLES_KEY):
            self.samples.append(sample(sample_json))

        # get patient/sample data components
        # TODO could allow patient/sample output to be configured independently
        # But for now, use the same config for both
        self.clinical_data = self.get_clinical_data(config.get(self.SAMPLES_META_KEY))



        self.genetic_alterations = []
        for genetic_alteration_json in config.get(self.GENETIC_ALTERATIONS_KEY):
            self.genetic_alterations.append(genetic_alteration(genetic_alteration_json))

    def get_clinical_data(self, samples_meta):
        sc = samples_component(self.samples, samples_meta, self.study_id)
        if samples_meta.get(self.WRITE_PATIENTS_KEY):
            pc = patients_component(self.samples, samples_meta, self.study_id)
        else:
            pc = None
        return [sc, pc]
    
    def get_case_lists(self, config):
        # generate default case lists based on pipelines in study:
        # - case lists for alteration_types MAF, SEG, MRNA_EXPRESSION
        # - only need one case list per alteration type (they may have multiple datatypes)
        # - cnaseq case list if CNA data and mutation data both present
        # - 3way_complete case list if CNA data, mutation data, expression data all present
        maf_key = utilities.constants.MAF_KEY
        seg_key = utilities.constants.SEG_KEY
        mrnax_key = utilities.constants.MRNA_EXPRESSION_KEY
        case_list_suffix_by_alteration_type = {
            maf_key: 'sequenced',
            seg_key: 'cna',
            mrnax_key: 'rna_seq_mrna'
        }
        case_lists = []
        generated = {}
        for pipeline in self.pipelines:
            alt_type = pipeline.get_name()
            suffix = case_list_suffix_by_alteration_type.get(alt_type)
            if suffix:
                name = pipeline.get_profile_name()
                description = pipeline.get_profile_description()
                samples = pipeline.get_sample_ids()
                if name!=None and description!=None and len(samples)>0:
                     case_lists.append(case_list(self.study_id, suffix, name, description, samples))
                     generated[alt_type] = pipeline
        if generated.get(maf_key) and generated.get(seg_key):
            self.logger.info("Generating cnaseq case list")
            suffix = 'cnaseq'
            samples_maf = set(generated[maf_key].get_sample_ids())
            samples_seg = set(generated[seg_key].get_sample_ids())
            samples_cnaseq = list(samples_maf & samples_seg) # intersection of samples
            name = 'Samples profiled for mutations and CNAs'
            description = 'Case list containing all samples profiled for mutations and CNAs'
            case_lists.append(case_list(self.study_id, suffix, name, description, samples_cnaseq))
            if generated.get(mrnax_key):
                self.logger.info("Generating 3way_complete case list")
                suffix = '3way_complete'
                samples_3wc = set(generated[mrnax_key].get_sample_ids()) & samples_cnaseq
                name = 'Samples profiled for mutations, CNAs, and mRNA expression'
                description = 'Case list containing all samples profiled for mutations, CNAs, '+\
                              'and mRNA expression'
                case_lists.append(case_list(self.study_id, suffix, name, description, samples_3wc))
        # generate custom case lists from config files
        case_list_config_paths = config.get_case_list_config_paths()
        for path in case_list_config_paths:
            case_lists.append(case_list.from_config_path(path, self.study_id))
        return case_lists

    def get_pipelines(self, config):
        config_paths = config.get_alterationtype_config_paths()
        alteration_types = []
        log_level = self.logger.getEffectiveLevel()
        for name in config_paths.keys():
            self.logger.debug("Found alteration type %s" % name)
            alteration_types.append(alteration_type(name, config_paths[name], config, log_level))
        if len(alteration_types) == 0:
            self.logger.warn("No pipeline data found for study %s" % self.study_id)
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

    def write_all(self, out_dir, dry_run=False, force=False):
        """Write all outputs to the given directory path"""
        # write component files
        valid = self.is_valid_output_dir(out_dir)
        if not valid:
            msg = "Invalid output directory %s; exiting" % out_dir
            self.logger.error(msg)
            raise OSError(msg)
        if len(os.listdir(out_dir)) > 0:
            prefix = "Output directory %s is not empty; " % out_dir
            if force:
                self.logger.info(prefix+"--force is in effect, removing directory contents.")
                rmtree(out_dir)
                os.mkdir(out_dir)
            else:
                 msg = prefix+"exiting. Run with --force to delete contents of directory."
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
            self.logger.debug("Found alteration type: "+str(pipeline.name))
            self.logger.debug("Found %i components" % len(pipeline.components))
            for component in pipeline.components:
                self.logger.debug("Writing output for component '%s'" % component.name)
                component.write(out_dir, dry_run)

