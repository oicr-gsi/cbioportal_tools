# Table of Contents

## Study Data
* [**STUDY_CONFIG.md**](STUDY_CONFIG.md)
* [CASE_LIST_CONFIG.md](CASE_LIST_CONFIG.md)
* [GENERAL_CONFIG.md](GENERAL_CONFIG.md)

### Mutation Data
This is probably what you are looking for...
* [MAF_CONFIG.md](MAF_CONFIG.md)
* [MRNA_EXPRESSION_CONFIG.md](MRNA_EXPRESSION_CONFIG.md)
* [SEGMENTED_CONFIG.md](SEGMENTED_CONFIG.md)
* [CONTINUOUS_COPY_NUMBER_CONFIG.md](CONTINUOUS_COPY_NUMBER_CONFIG.md)
* [DISCRETE_COPY_NUMBER_CONFIG.md](DISCRETE_COPY_NUMBER_CONFIG.md)

### Clinical Data
* [PATIENT_AND_**SAMPLE_CONFIG.md**](PATIENT_AND_SAMPLE_CONFIG.md)
* [TIMELINE_CONFIG.md](TIMELINE_CONFIG.md)

## cBioPortal Data
* [CANCER_TYPE_CONFIG.md](CANCER_TYPE_CONFIG.md)

# Minimal Study

Instructions for a minimal study are as follows.

1. Create a `study.txt` file that is of the type [**study_config**](STUDY_CONFIG.md)
   * Within the file give a unique `study_id`
   * Fill in the rest of the header with valid information
   * Inside the data-frame point to `samples.txt` with type `SAMPLE_ATTRIBUTES`
2. Create a `samples.txt` file that is of the type [**samples_config**](PATIENT_AND_SAMPLE_CONFIG.md#sample-attributes)
   * Minimal columns are `Patent Identifier` and `Sample Identifier`
3. **IF** the cancer-type of the study is not already present in cBioPortal, create a `cancer_type.txt` file of type [**cancer_type_config**](CANCER_TYPE_CONFIG.md)
   * Within `study.txt`'s data-frame, point to `cancer_type.txt` with type `CANCER_TYPE`