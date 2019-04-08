# CONTINUOUS COPY NUMBER Config
This is the specification for the `CONTINUOUS_COPY_NUMBER` study config file.

This file may follow the [standard format](STUDY_CONFIG.md).

### Configuring your data

You need to generate the segmented data from the [SEGMENTED_CONFIG.txt](SEGMENTED_CONFIG.md) pipeline to use the `SEG` pipeline. The definition for the `FILE` pipeline still needs to be figured out.

### Configuring your header

The minimal header will look like this:
```
#pipeline=[ SEG | FILE ]
#bed_file=/.mounts/labs/gsiprojects/gsi/cBioGSI/kchandan/cBioWrap/testdata/ncbi_genes_hg19_canonical.bed
#profile_name=Log2 copy-number values
#profile_description=Log2 copy-number values
```
All key-value pairs **above** are **required**.

## Adding Continuous Copy Number Data

To add **Continuous Copy Number Data** you need to add the key `CONTINUOUS_COPY_NUMBER` with the relative path to the mutation config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
CONTINUOUS_COPY_NUMBER	continuous.txt
```
The file `continuous.txt` could look like:

```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=SEG
#bed_file=/.mounts/labs/gsiprojects/gsi/cBioGSI/kchandan/cBioWrap/testdata/ncbi_genes_hg19_canonical.bed
#profile_name=Log2 copy-number values
#profile_description=Log2 copy-number values
```

# TODO:: Should there be a dataframe of patient and sample ID to include/not include