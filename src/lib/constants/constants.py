__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# TODO:: Add all the other data_types even if they are not implemented...
# To support other data_types, they need to be added to
#       meta_info_map
#       args2config_map
#       config2name_map

# meta_info_map is an ordered set corresponding to gene_id_zip. This generates the meta files for each data_type
meta_info_map = {'PATIENT_ATTRIBUTES':      ['CLINICAL', 'PATIENT_ATTRIBUTES'],
                 'SAMPLE_ATTRIBUTES':       ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 ## TODO:: IMPLEMENT TIMELINE
                 'TIMELINE':                ['CLINICAL', 'TIMELINE'],
                 'CANCER_TYPE':             ['CANCER_TYPE', 'CANCER_TYPE'],
                 'MAF':                     ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
                 'SEG':                     ['COPY_NUMBER_ALTERATION', 'SEG', 'hg19'],
                 'SEG_CNA':                 ['COPY_NUMBER_ALTERATION', 'DISCRETE', 'gistic', 'true'],
                 'SEG_LOG2CNA':             ['COPY_NUMBER_ALTERATION', 'LOG2-VALUE', 'log2CNA', 'true'],
                 'MRNA_EXPRESSION':         ['MRNA_EXPRESSION', 'CONTINUOUS', 'rna_seq_mrna', 'true'],
                 'MRNA_EXPRESSION_ZSCORES': ['MRNA_EXPRESSION', 'Z-SCORE', 'rna_seq_mrna_median_Zscores', 'true'],
                 ## TODO:: IMPLEMENT AND VERIFY AFTER THIS LINE
                 'DISCRETE_COPY_NUMBER':    ['UNIMPLEMENTED'],
                 'CONTINUOUS_COPY_NUMBER':  ['UNIMPLEMENTED'],
                 'FUSION':                  ['FUSION', 'FUSION', 'fusion', 'true'],
                 'METHYLATION':             ['METHYLATION', 'CONTINUOUS', 'methylation_hm27', 'false'],
                 'PROTEIN':                 ['PROTEIN_LEVEL', 'UNIMPLEMENTED', 'UNIMPLEMENTED', 'UNIMPLEMENTED'],
                 'GISTIC_2.0':              ['UNIMPLEMENTED'],
                 'MUTSIG':                  ['UNIMPLEMENTED'],
                 'GENE_PANEL':              ['UNIMPLEMENTED'],
                 'GENE_SET':                ['UNIMPLEMENTED']}


# args2config_map is for ensuring that the optional command line inputs for configuration files are imported
args2config_map = {'sample_info':           'SAMPLE_ATTRIBUTES',
                   'patient_info':          'PATIENT_ATTRIBUTES',
                   'timeline_info':         'TIMELINE',
                   'cancer_type':           'CANCER_TYPE',
                   'mutation_data':         'MAF',
                   'segmented_data':        'SEG',
                   'expression_data':       'MRNA_EXPRESSION',
                   ## TODO:: Not Implemented below this
                   'CNA_data':              'DISCRETE_COPY_NUMBER',
                   'log2CNA_data':          'CONTINUOUS_COPY_NUMBER',
                   'fusions_data':          'FUSION',
                   'methylation_hm27_data': 'METHYLATION',
                   'rppa_data':             'PROTEIN',
                   'gistic_genes_amp_data': 'GISTIC_2.0',
                   'mutsig_data':           'MUTSIG',
                   ## No idea what's going on with these two
                   'GENE_PANEL_data':            'GENE_PANEL',
                   'gsva_scores_data':           'GENE_SET'}

# config2name_map is used for creating the meta_{name}.txt and data_{name}.txt file names.
# This is especially useful when overwriting cBioWrap generated files
config2name_map = {'SAMPLE_ATTRIBUTES':       'clinical_samples',
                   'PATIENT_ATTRIBUTES':      'clinical_patients',
                   'CANCER_TYPE':             'cancer_type',
                   'MAF':                     'mutations_extended',
                   'SEG':                     'segments',
                   'SEG_CNA':                 'CNA',
                   'SEG_LOG2CNA':             'log2CNA',
                   'MRNA_EXPRESSION':         'expression',
                   'MRNA_EXPRESSION_ZSCORES': 'expression_zscores',
                   ## TODO:: Not Implemented below this
                   'DISCRETE_COPY_NUMBER':    'CNA',
                   'CONTINUOUS_COPY_NUMBER':  'log2CNA',
                   'FUSION':                  'fusions',
                   'METHYLATION':             'methylation_hm27',
                   'PROTEIN':                 'rppa',
                   'GISTIC_2.0':              'gistic_genes_amp',
                   'MUTSIG':                  'mutsig',
                   ## No idea what's going on with these two
                   'GENE_PANEL':              'GENE_PANEL',
                   'GENE_SET':                'gsva_scores'}


# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4
# A set of default ordered values all meta files have to a certain extent
general_zip =     ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']

ref_gene_id_zip = ['genetic_alteration_type', 'datatype', 'reference_genome_id']

case_list_map =   {'MAF':               '_sequenced',
                   'SEG':               '_cna',
                   'MRNA_EXPRESSION':   '_rna_seq_mrna'}
#TODO:: ensure correct suffixes
# https://cbioportal.readthedocs.io/en/latest/File-Formats.html#case-list-stable-id-suffixes

supported_vcf = ['Strelka', 'Mutect', 'Mutect2', 'MutectStrelka', 'GATKHaplotypeCaller']
supported_seg = ['CNVkit', 'Sequenza', 'HMMCopy']
supported_rna = ['Cufflinks', 'RSEM']
clinical_type = ['PATIENT_ATTRIBUTES', 'SAMPLE_ATTRIBUTES', 'TIMELINE']

# hg_19 chromosome lengths. (for fixing HMMCopy only?)
# First index of list is chromosome, second is the real value
hmmcopy_chrom_positions = 'hmmcopy_chrom_positions.txt'

cbioportal_ip = '10.30.133.80'
cbioportal_url = 'cbioportal.gsi.oicr.on.ca'
