# PATIENT_ATTRIBUTES & SAMPLE_ATTRIBUTES Config

This is the specification for the `PATIENT_ATTRIBUTES` & `SAMPLE_ATTRIBUTES` study config files.

Both files follow the [standard format](STUDY_CONFIG.md).

The `SAMPLE_ATTRIBUTES` file is the only required file for a study. 

The `PATIENT_ATTRIBUTES` is required for [TIMELINE_CONFIG.txt](TIMELINE_CONFIG.md) data.
It is also required for the Patient View, and showing other relevant information.
### Configuring your data

There are no files to which these data files will connect to. As such, it is simply a matter of getting the format right.

### Configuring your header

The header will look like this:
```
#profile_name=All samples/patients
#profile_description=All Study Samples/Patients (XX Samples/Patients)
```
All key-value pairs are required. 

### Configuring DataFrame

Each Attributes DataFrame has a 5 line header, where:

* Row **1**: The Display Names: The display name for each clinical attribute
* Row **2**: The Descriptions: Long(er) description of each clinical attribute
* Row **3**: The Datatype: The datatype of each clinical attribute (must be one of: \[ STRING | NUMBER | BOOLEAN \] )
* Row **4**: The Priority: Higher number corresponds to representation further up (not important, set to 1)
* Row **5**: The Column name: This name should be in all CAPS.

#### Patient Attributes

The DataFrame of the `PATIENTS_ATTRIBUTES` Config must contain these columns:
```
Patient Identifier	Patient Name
Patient Identifier	Patient Name
STRING	STRING
1	1
PATIENT_ID	PATIENT_DISPLAY_NAME
```

More columns can be added easily, the specially handled values for the columns are:
* `PATIENT_ID `(required): a unique patient ID.
* `PATIENT_DISPLAY_NAME`(required): Patient display name (string)
* `OS_STATUS`: Overall patient survival status \[ DECEASED | LIVING \]
* `OS_MONTHS`: Overall survival in months since initial diagnosis
* `DFS_STATUS`: Disease free status since initial treatment \[ DiseaseFree | Recurred | Progressed \]
* `DFS_MONTHS`: Disease free (months) since initial treatment
* `GENDER `or `SEX`: Gender or sex of the patient (string)
* `AGE`: Age at first diagnosed, in years (number)
* `TUMOR_SITE`: (string)
* Any other column name can be given as well to represent other data.

#### Sample Attributes

The DataFrame of the `SAMPLE_ATTRIBUTES` Config must contain these columns:

```
Patient Identifier	Sample Identifier
Patient Identifier	Sample Identifier
STRING	STRING
1	1
PATIENT_ID	SAMPLE_ID
```

More columns can be added easily, the specially handled values for the columns are:
* `PATIENT_ID `(required): A patient ID.
* `SAMPLE_ID `(required): A sample ID.
* `CANCER_TYPE`: Cancer Type
* `CANCER_TYPE_DETAILED`: Cancer Type Detailed
* `SAMPLE_DISPLAY_NAME`: displayed in addition to the ID
* `SAMPLE_CLASS`: ???
* `METASTATIC_SITE `or PRIMARY_SITE: Override TUMOR_SITE (patient level attribute)
* `OTHER_SAMPLE_ID`: an alias to the sample, To ensure that the timeline data field is correctly linked to this sample, be sure to add this column
* `SAMPLE_TYPE`, TUMOR_TISSUE_SITE or TUMOR_TYPE: gives sample icon in the timeline a color.
  * If set to recurrence, recurred, progression or progressed: orange
  * If set to metastatic or metastasis: red
  * If set to primary or otherwise: black
* Any other column name can be given as well to represent other data.

Note that the `PATIENT_ID` and `SAMPLE_ID` will show up in cBioPortal. Therefore `PATIENT_ID` and `SAMPLE_ID` must match that seen in all your data files.

## Adding PATIENT_ATTRIBUTES and/or SAMPLE_ATTRIBUTES Data

To add **PATIENT_ATTRIBUTES and/or SAMPLE_ATTRIBUTES Data** you need to add the key `PATIENT_ATTRIBUTES` and/or `SAMPLE_ATTRIBUTES` with the relative path to the clinical config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
PATIENT_ATTRIBUTES	patient.txt
SAMPLE_ATTRIBUTES	sample.txt
```
The file `patient.txt` could look like:

```
#profile_name=All Patients
#profile_description=All TEST Patients (5 Patients)
Patient Identifier	Patient Name	Sex	Age
Patient Identifier	Patient Name	Sex	Age
STRING	STRING	STRING	NUMBER
1	1	1	1
PATIENT_ID	PATIENT_DISPLAY_NAME	SEX	AGE
TEST_0001	PID_TEST_C_M_0001	Male	71
TEST_0002	PID_TEST_C_F_0002	Female	38
TEST_0003	PID_TEST_C_F_0003	Female	62
TEST_0004	PID_TEST_C_M_0004	Male	46
TEST_0005	PID_TEST_C_M_0005	Male	45
```
The file `sample.txt` could look like:

```
#profile_name=All Samples
#profile_description=All TEST Samples (5 Sample)
Patient Identifier	Sample Identifier
Patient Identifier	Sample Identifier
STRING	STRING
1	1
PATIENT_ID	SAMPLE_ID
TEST_0001	TEST_0001_TUMOR
TEST_0002	TEST_0002_TUMOR
TEST_0003	TEST_0003_TUMOR
TEST_0004	TEST_0004_TUMOR
TEST_0005	TEST_0005_TUMOR
```