# CANCER_TYPE Config

This is the specification for the `CANCER_TYPE` study config file.

This file mostly follows the [standard format](STUDY_CONFIG.md).

cBioPortal does not come with a set of pre-configured cancer-types, as such when adding a study you will almost always need to generate this file.

Multiple cancer-types can be added at once, this is especially useful if your study has multiple cancer types in it.

## File Configuration

The cancer-type file is a simple **TSV** with headers and no index. The 3 headers are:
```
NAME	CLINICAL_TRIAL_KEYWORDS	PARENT_TYPE_OF_CANCER
```

* The `NAME` value can have spaces
* The `CLINICAL_TRIAL_KEYWORDS` is a `CSV` list of keywords
* The `PARENT_TYPE_OF_CANCER` can have values other than tissue, but I've never tried that

Thus a completed file can look like:

```
NAME	CLINICAL_TRIAL_KEYWORDS	PARENT_TYPE_OF_CANCER
cancer A	very bad, cardiac, heart	tissue
cancer B	not as bad, cardiac, malignant	tissue
cancer C	even worse, carcinoma, cardiac	tissue
```

## Adding Cancer_Type Data

To add **Cancer_Type Data** you need to add the key `CANCER_TYPE` with the relative path to the Cancer_Type config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
CANCER_TYPE	cancer_type.txt
```