# Study Input Specification

The minimum required files for an importable study in cBioPortal are:
- `study.txt`
- `samples.txt`
- `case_lists/cases_all.txt`
- `cancer_type.txt` *

To generate this you will need a:
* [`study.txt`](Specification/STUDY_CONFIG.md)
* [`samples.txt`](Specification/PATIENT_AND_SAMPLE_CONFIG.md)
* [`cancer_type.txt`](Specification/CANCER_TYPE_CONFIG.md)*

*If the cancer type is not already in the cBioPortal instance database.

As of this commit, the supported importable types are:
* `SAMPLE_ATTRIBUTES`
* `PATIENT_ATTRIBUTES`
* `CANCER_TYPE`
* `MAF`
* `SEG`
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
