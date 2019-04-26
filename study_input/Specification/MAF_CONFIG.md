# MAF Config
This is the specification for the `MAF` and `VCF` study config files.

This file follows the [standard format](STUDY_CONFIG.md).

### Configuring your data
To add this type of data to the study, gather absolute paths to all your files (or symlinks) and ensure they are all of either **VCF or MAF** format, otherwise it will break.

If your files are compressed with any format, ensure it has the **correct extension**, (e.g. `*.tar.gz`, `*.zip`, `*.gz`), otherwise it will break.

### Configuring your header

The header will look like this:
```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=[ Strelka | Mutect | Mutect2 | MutectStrelka | GATKHaplotypeCaller | MAF | FILE ]
#profile_name=Mutations (Cardiac Cancer)
#profile_description=Mutation data from whole exome sequencing of cardiac tissue. (XX Samples)
#ref_fasta=/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa
#filter_vcf=/.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz
```
All key-value pairs are required. 

The program by **default** expects **VCF** format files, should you have already generated the **MAF** files and you want to import them without vcf2maf, you **MUST** make `MAF` the pipeline.

It is fine if the pipeline is unknown if files are of the format **MAF** however, it is required for **VCF**.
This is because **VCF** files require processing with `vcf2maf.pl` and prep is required for the different formats.

### Configuring DataFrame

The DataFrame of the `MAF` Config must contain these columns:

```
FILE_NAME	PATIENT_ID	NORMAL_ID	SAMPLE_ID	NORMAL_COL**	TUMOR_COL**
```

**Where the `NORMAL_COL` and `TUMOR_COL` are optional depending on the pipeline:

|Pipeline	|Optional columns required?	|
|---------------|-------------------------------|
|Mutect		|YES				|
|Mutect2	|NO				|
|Strelka	|YES				|
|Anything Else	|PROBABLY			|

Note that the `PATIENT_ID` and `SAMPLE_ID` will show up in cBioPortal, whereas the `NORMAL_ID` will not as it's only used for conversion.
Therefore `PATIENT_ID` and `SAMPLE_ID` must match that seen in [PATIENT_AND_SAMPLE_CONFIG.txt](PATIENT_AND_SAMPLE_CONFIG.md).

### Tumor Only Samples
If you have tumor-only samples that you would like to process, normally a duplicate column is added of the `SAMPLE_ID` and renamed `UNMATCHED`. However this process has been automated by Janus.
Should you have tumor-only samples:

* In the `MAF` config, set the `NORMAL_ID` `UNMATCHED` for the sample
* If you have a `NORMAL_COL` set it to `UNMATCHED` as well

Example:
```
...
FILE_NAME	PATIENT_ID	NORMAL_ID	SAMPLE_ID	NORMAL_COL	TUMOR_COL
tumor_only.vcf	TEST_0001	UNMATCHED	TEST_0001	UNMATCHED	CARD_0001
...
```
or
```
...
FILE_NAME	PATIENT_ID	NORMAL_ID	SAMPLE_ID
tumor_only.vcf	TEST_0001	UNMATCHED	TEST_0001
...
```

## Adding Mutation Data

To add **Mutation Data** you need to add the key `MAF` with the relative path to the mutation config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
MAF	mutation.txt
```
The file `mutation.txt` would look like:

```
#input_folder=/FOLDER/WITH/DATA/
#pipeline=Mutect
#profile_name=Mutations (Cardiac Cancer)
#profile_description=Mutation data from whole exome sequencing of cardiac tissue. (XX Samples)
#ref_fasta=/.mounts/labs/PDE/data/gatkAnnotationResources/hg19_random.fa
#filter_vcf=/.mounts/labs/gsiprojects/gsi/cBioGSI/data/reference/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz
FILE_NAME	PATIENT_ID	NORMAL_ID	SAMPLE_ID	NORMAL_COL	TUMOR_COL
TEST_0001.vcf.gz	TEST_0001	TEST_0001_N	TEST_0001_T	TEST_0001_NORMAL	TEST_0001_TUMOR
TEST_0002.vcf.gz	TEST_0002	TEST_0002_N	TEST_0002_T	TEST_0002_NORMAL	TEST_0002_TUMOR
```
- All `data_` type files can be directly imported into the study folder by:
  - Adding `#pipeline=FILE` to the header
  - Having the `dataframe` set as:
  ```
  FILE_NAME
  <LOCATION/OF/FILE.txt>
  ```
  Janus will rename it correctly.