# General Format

The format for all config files will be the same, there are **2 exceptions** to the rule:

- `CANCER_TYPE`
- `STUDY_CONFIG`

However it still shares a majority of it's attributes with the rest of the config files.

- All files are `TSV` (tab-separated-values)
- All files excluding [`CANCER_TYPE`.txt](CANCER_TYPE_CONFIG.md) has a header of key-value pairs where each line begins with `#` and pairs are separated by `=`
- All files excluding [`CANCER_TYPE`.txt](CANCER_TYPE_CONFIG.md) and [`STUDY_CONFIG`.txt](STUDY_CONFIG.md) have the columns `PATIENT_ID` AND `SAMPLE_ID`

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
