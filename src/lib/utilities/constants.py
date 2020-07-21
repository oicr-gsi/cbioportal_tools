"""Module to define constants"""

ALTERATION_TYPE_KEY = 'ALTERATIONTYPE'
DATAHANDLER_KEY = 'DATAHANDLER'
FILE_NAME_KEY = 'FILE_NAME'

CANCER_TYPE_DATATYPE = 'CANCER_TYPE'
CASE_LIST_DATATYPE = 'CASE_LIST'
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
