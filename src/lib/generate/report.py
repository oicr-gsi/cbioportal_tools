import json
import logging
from utilities.base import base

class report(base):

    """Class representing a genome interpretation Clinical Report"""

    CLINICAL_DATA_KEY = 'ClinData'
    GENOMIC_LANDSCAPE_KEY = 'genomicLandscape'
    SMALL_MUTATION_INDEL_KEY = 'smallMutAndIndel'
    GENE_KEY = 'Gene' # TODO move to utilities.constants

    def __init__(self, sample, alterations, log_level=logging.WARNING, log_path=None):
        self.logger = self.get_logger(log_level, "%s.%s" % (__name__, type(self).__name__), log_path)
        self.sample = sample
        self.sample_id = self.sample.get_id()
        self.alterations = alterations

    def get_report_config(self):
        """Construct the reporting config data structure"""
        config = {}
        config[self.GENOMIC_LANDSCAPE_KEY] = {}
        smi_results_by_gene = {} # small mutations and indels
        # for each genetic alteration, find values for smallMutAndIndel (if any) and update
        for alteration in self.alterations:
            # find small mutation and indel data
            smi_data = alteration.get_small_mutation_indel_data(self.sample_id)
            for gene_result in smi_data:
                gene_name = gene_result[self.GENE_KEY]
                if gene_name in smi_results_by_gene:
                    smi_results_by_gene[gene_name].update(gene_result)
                else:
                    smi_results_by_gene[gene_name] = gene_result
            self.sample.update_attributes(alteration.get_attributes_for_sample(self.sample_id))
        # sort the results by gene name
        smi_sorted = [smi_results_by_gene[k] for k in sorted(smi_results_by_gene.keys())]
        config[self.GENOMIC_LANDSCAPE_KEY][self.SMALL_MUTATION_INDEL_KEY] = smi_sorted
        config[self.CLINICAL_DATA_KEY] = self.sample.get_attributes()
        # TODO add other parts of the "genomic landscape", eg. oncoKB SVs & CNVs
        # TODO add other elements of report JSON, eg. "SVandFus", "exprOutliers"
        return config

    def write_report_config(self, out_path):
        with open(out_path, 'w') as out:
            out.write(json.dumps(self.get_report_config(), sort_keys=True, indent=4))
