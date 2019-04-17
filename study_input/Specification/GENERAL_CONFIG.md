# General Format

The format for all config files will be the same, there are a **few exceptions** to the rule:

- `CANCER_TYPE`
- `STUDY_CONFIG`
- `DISCRETE_COPY_NUMBER`
- `CONTINUOUS_COPY_NUMBER`
- `MRNA_EXPRESSION_ZSCORES`

However it still shares a majority of it's attributes with the rest of the config files.

- All files are `TSV` (tab-separated-values)

- All files excluding [`CANCER_TYPE.txt`](CANCER_TYPE_CONFIG.md) has a header of key-value pairs where each line begins with `#` and pairs are separated by `=`

- All files excluding [`CANCER_TYPE.txt`](CANCER_TYPE_CONFIG.md), [`STUDY_CONFIG.txt`](STUDY_CONFIG.md), 
[`DISCRETE_COPY_NUMBER.txt`](DISCRETE_COPY_NUMBER_CONFIG.md), [`CONTINUOUS_COPY_NUMBER.txt`](CONTINUOUS_COPY_NUMBER_CONFIG.md), 
[`MRNA_EXPRESSION.txt`](MRNA_EXPRESSION_CONFIG.md), have the columns `PATIENT_ID` AND `SAMPLE_ID`

- All files excluding [`DISCRETE_COPY_NUMBER.txt`](DISCRETE_COPY_NUMBER_CONFIG.md), [`CONTINUOUS_COPY_NUMBER.txt`](CONTINUOUS_COPY_NUMBER_CONFIG.md), 
[`MRNA_EXPRESSION.txt`](MRNA_EXPRESSION_CONFIG.md) must have the TSV dataframe

- All `data_` type files can be directly imported into the study folder by:
  - Adding `#pipeline=FILE` to the header
  - Having the `dataframe` set as:
  ```
  FILE_NAME
  <LOCATION/OF/FILE.txt>
  ```
  Janus will rename it correctly.

  
Therefore we can generate a general format that looks like this:

The form of all configuration files is essentially

```
#property=value
#other_property=Something relavent
#description=Relevant description (12 Samples)
...
FILE_NAME	PATIENT_ID	SAMPLE_ID		...
Val_01.txt	GSI_0001	GSI_0001_TUMOR_01	...
Val_01.txt	GSI_0001	GSI_0001_NORMAL_01	...
...
```

This form is absorbed into an object of type `Config` this object has 3 components:

```
config_map: dict
data_frame: pandas.DataFrame
type_config: str
```