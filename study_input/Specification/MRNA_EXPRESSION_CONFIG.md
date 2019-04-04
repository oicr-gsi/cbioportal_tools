# MRNA_EXPRESSION Config
This is the specification for the `MRNA_EXPRESSION` study config files.

This file follows the [standard format](STUDY_CONFIG.md).

### Configuring your data
To add this type of data to the study, gather absolute paths to all your files (or symlinks) and ensure they all contain an `FPKM` column, otherwise it will break.

If your files are compressed with any format, ensure it has the **correct extension**, (e.g. `*.tar.gz`, `*.zip`, `*.gz`), otherwise it will break.

### Configuring your header

The header will look like this:
```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=[ Cufflinks, RSEM ]
#profile_name=mRNA Expression
#profile_description=Expression information (XX Samples)
```
All key-value pairs are required. 

### Configuring DataFrame

The DataFrame of the `MRNA_EXPRESSION` Config must contain these columns:

```
FILE_NAME	PATIENT_ID	SAMPLE_ID
```

Note that the `PATIENT_ID` and `SAMPLE_ID` will show up in cBioPortal. Therefore `PATIENT_ID` and `SAMPLE_ID` must match that seen in [PATIENT_AND_SAMPLE_CONFIG.txt](PATIENT_AND_SAMPLE_CONFIG.md).

## Adding Expression Data

To add **Expression Data** you need to add the key `MRNA_EXPRESSION` with the relative path to the expression config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
MRNA_EXPRESSION	expression.txt
```
The file `expression.txt` would look like:

```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=Cufflinks
#profile_name=mRNA Expression
#profile_description=Expression information (XX Samples)
FILE_NAME	PATIENT_ID	SAMPLE_ID
TEST_0001.vcf.gz	TEST_0001	TEST_0001_T
TEST_0002.vcf.gz	TEST_0002	TEST_0002_N
```