# SEGMENTATION Config
This is the specification for the `SEG` study config file.

This file follows the [standard format](STUDY_CONFIG.md).

### Configuring your data
To add this type of data to the study, gather absolute paths to all your files (or symlinks) and ensure they are all from one **SEG** pipeline, otherwise lots of **data** will be **lost**.

If your files are compressed with any format, ensure it has the **correct extension**, (e.g. `*.tar.gz`, `*.zip`, `*.gz`), otherwise it will break.

Please keep in mind that the `.bed` file you need **must** have its **headers**.

### Configuring your header

The minimal header will look like this:
```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=[ CNVkit | Sequenza | HMMCopy | FILE ]
#profile_name=Segmentation Mutations (Cardiac Cancer)
#profile_description=Segmentation data from whole exome sequencing of cardiac tissue. (XX Samples)
#bed_file=/.mounts/labs/gsiprojects/gsi/cBioGSI/kchandan/cBioWrap/testdata/ncbi_genes_hg19_canonical.bed
```
All key-value pairs **above** are **required**.

### Configuring DataFrame

The DataFrame of the `SEG` Config must contain these columns:

```
FILE_NAME	PATIENT_ID	SAMPLE_ID
```

Note that the `PATIENT_ID` and `SAMPLE_ID` will show up in cBioPortal. Therefore `PATIENT_ID` and `SAMPLE_ID` must match that seen in [PATIENT_AND_SAMPLE_CONFIG.txt](PATIENT_AND_SAMPLE_CONFIG.md).

## Adding Segmentation Data

To add **Segmentation Data** you need to add the key `SEG` with the relative path to the mutation config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
SEG	segmented.txt
```
The file `segmented.txt` could look like:

```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=Sequenza
#profile_name=Mutations (Cardiac Cancer)
#profile_description=Mutation data from whole exome sequencing of cardiac tissue. (XX Samples)
#bed_file=/.mounts/labs/gsiprojects/gsi/cBioGSI/kchandan/cBioWrap/testdata/ncbi_genes_hg19_canonical.bed
FILE_NAME	PATIENT_ID	SAMPLE_ID
TEST_0001.tsv	TEST_0001	TEST_0001_TUMOR
TEST_0001.tsv	TEST_0002	TEST_0002_TUMOR
```
- All `data_` type files can be directly imported into the study folder by:
  - Adding `#pipeline=FILE` to the header
  - Having the `dataframe` set as:
  ```
  FILE_NAME
  <LOCATION/OF/FILE.txt>
  ```
  Janus will rename it correctly.