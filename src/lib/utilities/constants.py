"""Module to define constants"""

PATIENT_DATATYPE = 'PATIENT_ATTRIBUTES'
SAMPLE_DATATYPE = 'SAMPLE_ATTRIBUTES'

REQUIRED_STUDY_META_FIELDS = [
    'type_of_cancer',
    'cancer_study_identifier',
    'name',
    'description',
    'short_name'
]

OPTIONAL_STUDY_META_FIELDS = [
    'citation',
    'pmid',
    'groups',
    'add_global_case_list',
    'tags_file'
]