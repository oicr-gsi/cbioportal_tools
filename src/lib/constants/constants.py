__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os

# To support other data_types, they need to be added to
#       meta_info_map
#       args2config_map
#       config2name_map
# If a set of data_types does not require a corresponding dataframe, add to:
#       no_data_frame

# meta_info_map is an ordered set corresponding to gene_id_zip. This generates the meta files for each data_type
meta_info_map = {'CLINICAL:PATIENT_ATTRIBUTES':      ['CLINICAL', 'PATIENT_ATTRIBUTES'],
                 'CLINICAL:SAMPLE_ATTRIBUTES':       ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
                 # TODO:: IMPLEMENT TIMELINE
                 'CLINICAL:TIMELINE':                ['CLINICAL', 'TIMELINE'],
                 'CANCER_TYPE:CANCER_TYPE':             ['CANCER_TYPE', 'CANCER_TYPE'],
                 'MUTATION_EXTENDED:MAF':                     ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
                 'COPY_NUMBER_ALTERATION:SEG':                     ['COPY_NUMBER_ALTERATION', 'SEG', 'hg19'],
                 'COPY_NUMBER_ALTERATION:DISCRETE':    ['COPY_NUMBER_ALTERATION', 'DISCRETE', 'gistic', 'true'],
                 'COPY_NUMBER_ALTERATION:CONTINUOUS':  ['COPY_NUMBER_ALTERATION', 'LOG2-VALUE', 'log2CNA', 'true'],
                 'MRNA_EXPRESSION:CONTINUOUS':         ['MRNA_EXPRESSION', 'CONTINUOUS', 'rna_seq_mrna', 'true'],
                 'MRNA_EXPRESSION:Z-SCORE': ['MRNA_EXPRESSION', 'Z-SCORE', 'rna_seq_mrna_median_Zscores', 'true'],
                 # TODO:: IMPLEMENT AND VERIFY AFTER THIS LINE
                 'FUSION:FUSION':                  ['FUSION', 'FUSION', 'fusion', 'true'],
                 'METHYLATION:CONTINUOUS':             ['METHYLATION', 'CONTINUOUS', 'methylation_hm27', 'false'],
                 'PROTEIN_LEVEL:':                 ['PROTEIN_LEVEL', 'UNIMPLEMENTED', 'UNIMPLEMENTED', 'UNIMPLEMENTED'],
                 'GISTIC_2':                ['UNIMPLEMENTED'],
                 'MUTSIG':                  ['UNIMPLEMENTED'],
                 'GENE_PANEL':              ['UNIMPLEMENTED'],
                 'GENE_SET':                ['UNIMPLEMENTED']}
#meta_info_map = {'PATIENT_ATTRIBUTES':      ['CLINICAL', 'PATIENT_ATTRIBUTES'],
#                 'SAMPLE_ATTRIBUTES':       ['CLINICAL', 'SAMPLE_ATTRIBUTES'],
#                 # TODO:: IMPLEMENT TIMELINE
#                 'TIMELINE':                ['CLINICAL', 'TIMELINE'],
#                 'CANCER_TYPE':             ['CANCER_TYPE', 'CANCER_TYPE'],
#                 'MAF':                     ['MUTATION_EXTENDED', 'MAF', 'mutations', 'true'],
#                 'SEG':                     ['COPY_NUMBER_ALTERATION', 'SEG', 'hg19'],
#                 'DISCRETE_COPY_NUMBER':    ['COPY_NUMBER_ALTERATION', 'DISCRETE', 'gistic', 'true'],
#                 'CONTINUOUS_COPY_NUMBER':  ['COPY_NUMBER_ALTERATION', 'LOG2-VALUE', 'log2CNA', 'true'],
#                 'MRNA_EXPRESSION':         ['MRNA_EXPRESSION', 'CONTINUOUS', 'rna_seq_mrna', 'true'],
#                 'MRNA_EXPRESSION_ZSCORES': ['MRNA_EXPRESSION', 'Z-SCORE', 'rna_seq_mrna_median_Zscores', 'true'],
#                 # TODO:: IMPLEMENT AND VERIFY AFTER THIS LINE
#                 'FUSION':                  ['FUSION', 'FUSION', 'fusion', 'true'],
#                 'METHYLATION':             ['METHYLATION', 'CONTINUOUS', 'methylation_hm27', 'false'],
#                 'PROTEIN':                 ['PROTEIN_LEVEL', 'UNIMPLEMENTED', 'UNIMPLEMENTED', 'UNIMPLEMENTED'],
#                 'GISTIC_2':                ['UNIMPLEMENTED'],
#                 'MUTSIG':                  ['UNIMPLEMENTED'],
#                 'GENE_PANEL':              ['UNIMPLEMENTED'],
#                 'GENE_SET':                ['UNIMPLEMENTED']}


# args2config_map is for ensuring that the optional command line inputs for configuration files are imported
args2config_map = {'sample_info':               'SAMPLE_ATTRIBUTES',
                   'patient_info':              'PATIENT_ATTRIBUTES',
                   'timeline_info':             'TIMELINE',
                   'cancer_type':               'CANCER_TYPE',
                   'mutation_data':             'MAF',
                   'segmented_data':            'SEG',
                   'expression_data':           'MRNA_EXPRESSION',
                   'expression_zscores_data':   'MRNA_EXPRESSION_ZSCORES',
                   'custom_case_list':          'CASE_LIST',
                   # TODO:: IMPLEMENT AND VERIFY AFTER THIS LINE
                   'continuous_data':           'CONTINUOUS_COPY_NUMBER',
                   'discrete_data':             'DISCRETE_COPY_NUMBER',
                   'fusion_data':               'FUSION',
                   'methylation_data':          'METHYLATION',
                   'protein_data':              'PROTEIN',
                   'gistic2_data':              'GISTIC2',
                   'mutsig_data':               'MUTSIG',
                   # No idea what's going on with these two
                   'gene_panel_data':           'GENE_PANEL',
                   'gene_set_data':             'GENE_SET'}

#config2name_map is used for creating the meta_{name}.txt and data_{name}.txt file names
## key for this should be the alterationtype:datatype
config2name_map = {'CLINICAL:SAMPLE_ATTRIBUTES':        'clinical_samples',
                   'CLINICAL:PATIENT_ATTRIBUTES':       'clinical_patients',
                   'CANCER_TYPE:CANCER_TYPE':           'cancer_type',
                   'MUTATION_EXTENDED:MAF':            'mutations_extended',
                   'COPY_NUMBER_ALTERATION:SEG':        'segments',
                   'COPY_NUMBER_ALTERATION:DISCRETE':   'CNA',
                   'COPY_NUMBER_ALTERATION:CONTINUOUS': 'log2CNA',
                   'MRNA_EXPRESSION:CONTINUOUS':        'expression_continous',
                   'MRNA_EXPRESSION:DISCRETE':          'expression_discrete',
                   'MRNA_EXPRESSION:Z-SCORE':           'expression_zscores',
                   # TODO:: IMPLEMENT AND VERIFY AFTER THIS LINE
                   'FUSION:FUSION':                     'fusion',
                   'METHYLATION:CONTINUOUS':            'methylation',
                   'PROTEIN_LEVEL:LOG2-VALUE':          'rppa',
                   'GISTIC_2':                          'gistic_genes_amp',
                   'MUTSIG:Q-VALUE':                    'mutsig',
                   # No idea what's going on with these two
                   'GENE_PANEL_MATRIX:GENE_PANEL_MATRIX':'GENE_PANEL',
                   'GENE_SET_SCORE:GSVA-SCORE':          'gsva_scores',
                   'GENE_SET_SCORE:P-VALUE':             'gsva_pvalues'}

#config2name_map = {'SAMPLE_ATTRIBUTES':       'clinical_samples',
#                   'PATIENT_ATTRIBUTES':      'clinical_patients',
#                   'CANCER_TYPE':             'cancer_type',
#                   'MAF':                     'mutations_extended',
#                   'SEG':                     'segments',
#                   'MRNA_EXPRESSION':         'expression',
#                   'MRNA_EXPRESSION_ZSCORES': 'expression_zscores',
#                   # TODO:: IMPLEMENT AND VERIFY AFTER THIS LINE
#                   'DISCRETE_COPY_NUMBER':    'CNA',
#                   'CONTINUOUS_COPY_NUMBER':  'log2CNA',
#                   'FUSION':                  'fusion',
#                   'METHYLATION':             'methylation',
#                   'PROTEIN':                 'rppa',
#                   'GISTIC_2':                'gistic_genes_amp',
#                   'MUTSIG':                  'mutsig',
#                   # No idea what's going on with these two
#                   'GENE_PANEL':              'GENE_PANEL',
#                   'GENE_SET':                'gsva_scores'}


# Keep note that a datatype will always have either:
# genetic_alteration_type & datatype; or
# genetic_alteration_type, datatype, stable_id & show_profile_in_analysis_tab:
# The exception is Expression Data which also has source_stable_id on top of the other 4
# A set of default ordered values all meta files have to a certain extent
general_zip =     ['genetic_alteration_type', 'datatype', 'stable_id', 'show_profile_in_analysis_tab']

ref_gene_id_zip = ['genetic_alteration_type', 'datatype', 'reference_genome_id']

optional_fields = ['groups', 'gene_panel', 'swissprot_identifier', 'variant_classification_filter', 'Protein_position',
                   'SWISSPROT', 'Fusion_Status', 'citation', 'pmid']

case_list_map =   {'MAF':               '_sequenced',
                   'SEG':               '_cna',
                   'MRNA_EXPRESSION':   '_rna_seq_mrna',
                   'CASE_LIST':         '_custom'}

#TODO:: ensure correct suffixes
# https://cbioportal.readthedocs.io/en/latest/File-Formats.html#case-list-stable-id-suffixes

no_data_frame = ['CONTINUOUS_COPY_NUMBER', 'DISCRETE_COPY_NUMBER', 'MRNA_EXPRESSION_ZSCORES']

#supported_pipe = {'MAF':                       ['MAF', 'Strelka', 'Mutect', 'Mutect2',
#                                                'MutectStrelka', 'GATKHaplotypeCaller'],
#                  'SEG':                       ['CNVkit', 'Sequenza', 'HMMCopy'],
#                  'MRNA_EXPRESSION':           ['Cufflinks', 'RSEM'],
#                  'MRNA_EXPRESSION_ZSCORES':   ['MRNA_EXPRESSION'],
#                  'CONTINUOUS_COPY_NUMBER':    ['SEG'],
#                  'DISCRETE_COPY_NUMBER':      ['CONTINUOUS_COPY_NUMBER']}

### this hash should be generated from the file hiearchy or from the import packages
supported_pipe = {'MUTATION_EXTENDED':            ['MAF', 'Strelka', 'Mutect', 'Mutect2',
                                                    'MutectStrelka', 'GATKHaplotypeCaller'],
                  'COPY_NUMBER_ALTERATION':       ['CNVkit', 'Sequenza', 'HMMCopy'],
                  'MRNA_EXPRESSION':              ['Cufflinks', 'RSEM']}
#                  'MRNA_EXPRESSION_ZSCORES':   ['MRNA_EXPRESSION'],
#                  'CONTINUOUS_COPY_NUMBER':    ['SEG'],
#                  'DISCRETE_COPY_NUMBER':      ['CONTINUOUS_COPY_NUMBER']}



clinical_type = ['PATIENT_ATTRIBUTES', 'SAMPLE_ATTRIBUTES', 'TIMELINE']

# hg_19 chromosome lengths. (for fixing HMMCopy only?)
# First index of list is chromosome, second is the real value
hmmcopy_chrom_positions = 'src/lib/constants/hmmcopy_chrom_positions.txt'
seg2gene = 'src/lib/data_type/seg2gene.R'
colours = 'src/lib/constants/cancer_colours.csv'

cbioportal_url = 'cbioportal-stage.gsi.oicr.on.ca'
