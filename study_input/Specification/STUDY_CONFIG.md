# Study Configuration file

You will most likely want to generate this file, but you don't need to, because **all** of its 
**functionality** can be **reproduced** on the **command line with the optional flags**. 

**All files** can be given **whatever name** you want to give them, but be sensible and give them useful names.

The main study file should be called `study.txt` and should look like this:

```
#type_of_cancer=<type of cancer (usually 1-3 words)>
#cancer_study_identifier=<study identifier (case sensitive)>
#name=<Full name (This is what shows up on the study view)>
#short_name=<Short name (no idea where this is used)>
#description=<Study description (no idea where this is used)>
#study_output_folder=<Arbitrary folder, use absolute path>
#cbioportal_key=<Portal Instance key(if required)>
TYPE	FILE_NAME
<SUPPORTED_TYPE>	<relative_path.txt>
```
### Working Example
A working example of the same file ...
```
#type_of_cancer=cardiac
#cancer_study_identifier=real_2019_study
#name=Real Study 2019 Cardiac
#short_name=CARDIAC
#description=Cardiac samples sequenced and analyzed at OICR
#study_output_folder=/STUDIES/REAL_STUDY/
#cbioportal_key=/u/kchandan/cbioportal.pem
TYPE	FILE_NAME
MRNA_EXPRESSION	expression.txt
MAF	mutation.txt
SEG	segmented.txt
SAMPLE_ATTRIBUTES	sample.txt
PATIENT_ATTRIBUTES	patient.txt
CANCER_TYPE	cancer_type.txt
```

### Minimum
The minimum required files to import a 'study' is:
```
#type_of_cancer=cardiac
#cancer_study_identifier=real_2019_study
#name=Real Study 2019 Cardiac
#short_name=CARDIAC
#description=Cardiac samples sequenced and analyzed at OICR
#study_output_folder=/STUDIES/REAL_STUDY/
TYPE	FILE_NAME
SAMPLE_ATTRIBUTES	sample.txt
```
**This assumes that there is no key required for the study instance or you don't want to upload it, 
and the cancer_type you are importing already exists in the instance database.**