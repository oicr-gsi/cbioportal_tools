__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# TODO:: Support all the other data types:
# To support other data_types, they need to be added to
#       meta_info_map
#       args2config_map
#       config2name_map

# meta_info_map is an ordered set corresponding to gene_id_zip. This generates the meta files for each data_type
meta_info_map = {'MAF':                   ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
                 'SEG':                   ['COPY_NUMBER_ALTERATION', 'SEG', 'hg19'],
                 'MRNA_EXPRESSION':       ['MRNA_EXPRESSION', 'CONTINUOUS', 'rna_seq_mrna', 'true'],
                 'SAMPLE_ATTRIBUTES':     ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 'PATIENT_ATTRIBUTES':    ['CLINICAL', 'PATIENT_ATTRIBUTES'],
                 'CANCER_TYPE':           ['CANCER_TYPE', 'CANCER_TYPE']}


# args2config_map is for ensuring that the optional command line inputs for configuration files are imported
args2config_map = {'mutation_data':        'MAF',
                   'segmented_data':       'SEG',
                   'expression_data':      'MRNA_EXPRESSION',
                   'sample_info':          'SAMPLE_ATTRIBUTES',
                   'patient_info':         'PATIENT_ATTRIBUTES',
                   'cancer_data':          'CANCER_TYPE'}

# config2name_map is used for creating the meta_{name}.txt and data_{name}.txt file names.
# This is especially useful when overwriting cBioWrap generated files
config2name_map = {'MAF':                     'mutations_extended',
                   'SEG':                     'segments',
                   'MRNA_EXPRESSION':         'expression',
                   'MRNA_EXPRESSION_ZSCORES': 'expression_zscores',
                   'SAMPLE_ATTRIBUTES':       'clinical_samples',
                   'PATIENT_ATTRIBUTES':      'clinical_patients',
                   'CANCER_TYPE':             'cancer_type'}


# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4
# A set of default ordered values all meta files have to a certain extent
general_zip =     ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']

ref_gene_id_zip = ['genetic_alteration_type', 'datatype', 'reference_genome_id']

case_list_map =   {'MAF':               '_sequenced',
                   'MRNA_EXPRESSION':   '_rna_seq_mrna'}

cbiowrap_export = ['MAF', 'SEG', 'MRNA_EXPRESSION']

# hg_19 chromosome lengths. (for fixing HMMCopy only?)
# First index of list is chromosome, second is the real value
hmmcopy_chrom_positions = 'hmmcopy_chrom_positions.txt'

cbioportal_url = '10.30.133.80'
cbioportal_port = '8080'
cbioportal_folder = 'cbioportal'