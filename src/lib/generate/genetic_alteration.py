
import logging
import random
from utilities.base import base

class genetic_alteration(base):
    """Base class; unit of genetic alteration data for cBioPortal"""

    # get_* methods are demonstration/placeholders only; will be overridden in subclasses
    
    GENETIC_ALTERATION_TYPE_KEY = 'genetic_alteration_type'
    DATATYPE_KEY = 'datatype'
    WORKFLOW_KEY = 'oicr_workflow'
    METADATA_KEY = 'metadata'
    INPUT_FILES_KEY = 'input_files'
    
    def __init__(self, config, log_level=logging.WARNING, log_path=None):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__), log_path)
        try:
            self.genetic_alteration_type = config[self.GENETIC_ALTERATION_TYPE_KEY]
            self.datatype = config[self.DATATYPE_KEY]
            self.workflow = config[self.WORKFLOW_KEY]
            self.metadata = config[self.METADATA_KEY]
            self.input_files = config[self.INPUT_FILES_KEY]
        except KeyError as err:
            self.logger.error("Missing required config key: {0}".format(err))
            raise
        self.sample_ids = sorted(self.input_files.keys())

    def get_cbioportal_data(self):
        """Placeholder; subclasses process the input files to get cBioPortal data table"""
        data = []
        data.append(['Sample ID', 'Input file', 'Comment'])
        for sample_id in self.sample_ids:
            data.append([sample_id, input_files[sample_id], "Placeholder; no metrics here"])
        return data

    def get_genes(self):
        """Placeholder; subclasses will read genes from input files"""
        return ["Gene001", "Gene002"]
    
    def get_small_mutation_indel_data(self, sample_id):
        """Placeholder; subclasses read results for gene & alteration type from input file"""
        input_file = self.input_files[sample_id]
        # generate dummy results as a demonstration
        metric_key = ":".join([self.genetic_alteration_type, self.datatype, 'dummy_metric'])
        data = []
        for gene in self.get_genes():
            data.append(
                {
                    "Gene": gene,
                    metric_key: random.randrange(1000)
                }
            )
        return data
