# Study Input Specification
The required input for the study is outlined here.

The minimum required files are:
- _study.txt_
- _samples.txt_
- _case_lists/cases_all.txt_
- _cancer_type.txt_ **

** If cancer type is not already in the database

Once they are filled they will produce the minimum required files.

The main study file should be called study.txt and should look like this:

```
#type_of_cancer=colorectal
#cancer_study_identifier=gecco_gsi_mutect_2019
#name=Genetics and Epidemiology of Colorectal Cancer Consortium
#short_name=GECCO
#description=GECCO Samples sequenced and analyzed at OICR
#study_output_folder=/.mounts/labs/gsiprojects/gsi/cBioGSI/data/snv/cbioMutect/
#cbioportal_key=/u/kchandan/cbioportal.pem
Type	File
mutation	mutation.txt
sample	sample.txt
```
There are a limited number of types. Although no error is currently thrown, it will possibly generate an error during the import step of cBioPortal.

As of this commit, the supported types are:
- `mutation`
- `segmented`
- `sample`
- `patient`
- `cancer_type`

Each one of these files can have any name that you desire, they simply need to have their relative path specified.


The breakdown of the form of all files is essentially
~~~
#Property=value
#profile_name=Something relavent (Required for)
#profile_description=Mutation data from whole exome sequencing. (12 Samples)
...
Col_Name	Patient_ID	Other_Relavent_Information
Value_01	GSI_0001	Blah_Blah
~~~

Each Data File that is added must also contain a ```Patient_ID``` column


## Example: Adding Mutation Data

To add **Mutation Data** you need to add ```mutation:mutation.txt``` to the bottom in TSV format. 

The format of the file will be:

```
#input_folder=/folder/
#caller=[Mutect | Mutect2 | Strelka | GATK]
#profile_name=Mutations (Colorectal)
#profile_description=Mutation data from whole exome sequencing.
File_Name	Patient_ID	Normal_col	Tumor_col	(Optional): Normal_ID	(Optional): Tumor_ID
File.vcf.gz	GECCO_0001	GECCO_0001_Ly_R_TS	GECCO_0001_Li_P_TS
```