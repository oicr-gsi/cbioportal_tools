# Study Input Specification

The minimum required files for an importable study in cBioPortal are:
- `study.txt`
- `samples.txt`
- `case_lists/cases_all.txt`
- `cancer_type.txt` *

*If the cancer type is not already in the cBioPortal instance database.

As of this commit, the supported importable types are:
* `SAMPLE_ATTRIBUTES`
* `PATIENT_ATTRIBUTES`
* `CANCER_TYPE`
* `MAF`
* `SEG`
* `SEG_CNA`
* `SEG_LOG2CNA`
* `DISCRETE_COPY_NUMBER`
* `CONTINUOUS_COPY_NUMBER`
* `MRNA_EXPRESSION` 
* `MRNA_EXPRESSION_ZSCORES`

The following types are stubs and need your help to implement: 

<!--- This is very important!! --->
<img src="https://upload.wikimedia.org/wikipedia/commons/d/df/Uncle_Sam_%28pointing_finger%29.png" width="100" height="134" />
<!--- This is very important!! --->

* `FUSION`
* `METHYLATION`
* `PROTEIN`
* `GISTIC_2.0`
* `MUTSIG`
* `GENE_PANEL`
* `GENE_SET`

Once the configuration files for the datatype are pointed to they will produce the required files for cBioPortal import.
