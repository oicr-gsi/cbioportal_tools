__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

meta_info_map = {'MAF': ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
                 'SEG': ['COPY_NUMBER_ALTERATION', 'SEG', 'hg19'],
                 'GEP': ['MRNA_EXPRESSION', 'CONTINUOUS'],
                 'SAMPLE_ATTRIBUTES': ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 'PATIENT_ATTRIBUTES': ['CLINICAL', 'PATIENT_ATTRIBUTES'],
                 'CANCER_TYPE': ['CANCER_TYPE', 'CANCER_TYPE']}

# TODO:: Add all the other data types.
# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4

# A set of default ordered values all meta files have to a certain extent
general_zip = ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']

ref_gene_id_zip = ['genetic_alteration_type', 'datatype', 'reference_genome_id']

case_list_map = {'MAF': '_sequenced',
                 'DISCRETE': '_cna'}

cbiowrap_export = ['MAF', 'SEG', 'GEP']

args2config_map = {'mutation_data': 'MAF',
                   'segmented_data': 'SEG',
                   'expression_data': 'GEP',
                   'sample_info': 'SAMPLE_ATTRIBUTES',
                   'patient_info': 'PATIENT_ATTRIBUTES',
                   'cancer_data': 'CANCER_TYPE'}

config2name_map = {'MAF': 'mutations_extended',
                   'SEG': 'segments',
                   'GEP': 'log2CNA',
                   'SAMPLE_ATTRIBUTES': 'clinical_samples',
                   'PATIENT_ATTRIBUTES': 'clinical_patients',
                   'CANCER_TYPE': 'cancer_type'}
# dCNA => discrete Copy Number Variation

# hg_19 chromosome lengths. (for fixing HMMCopy only?)
# First index of list is chromosome, second is the real value
hmmcopy_chrom_positions = 'hmmcopy_chrom_positions.txt'