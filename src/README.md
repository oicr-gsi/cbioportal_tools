# _src_ folder

Run with ```./runner.sh``` all arguments can be modified:

### Detailed help:

```
usage: janus.py [-h] [-o FOLDER] [-c FILE] [-t TYPE] [-i ID] [-N NAME]
                [-n NAME] [-d DESCRIPTION] [-k FILE] [-p] [-v] [-f]

janus (https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate
an importable study for a cBioPortal instance. Recommended usage can be seen
in the examples located in ../study_input/ .

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        The location of the study config file, containing
                        command line arguments as key/value pairs
  -o FOLDER, --output-folder FOLDER
                        The main folder of the study you want to generate.
  -t TYPE, --type-of-cancer TYPE
                        The type of cancer.
  -i ID, --cancer-study-identifier ID
                        The cancer study ID.
  -N NAME, --name NAME  The name of the study.
  -n NAME, --short-name NAME
                        A short name for the study.
  -d DESCRIPTION, --description DESCRIPTION
                        A description of the study.
  -k FILE, --key FILE   The RSA key to cBioPortal. Should have appropriate
                        read write restrictions
  -p, --push            Push the generated study to the cBioPortal Instance
  -v, --verbose         Makes program verbose
  -f, --force           Forces overwriting of data_cancer_type.txt file and
                        *.maf files.

OPTIONAL Configuration File Specifiers:
  --mutation-data MUTATION_DATA
                        Location of mutation_data configuration file.
  --segmented-data SEGMENTED_DATA
                        Location of segmented_data configuration file.
  --expression-data EXPRESSION_DATA
                        Location of expression_data configuration file.
  --sample-info SAMPLE_INFO
                        Location of sample_info configuration file.
  --patient-info PATIENT_INFO
                        Location of patient_info configuration file.
  --cancer-data CANCER_DATA
                        Location of cancer_data configuration file.

```
### Examples:
```
python3.6 janus.py \
			--output-folder /.mounts/labs/gsiprojects/gsi/cBioGSI/data/project_TEST/cbio_DCIS/ \
			--config ../study_input/DCIS/study.txt \
			--type-of-cancer 'ductal carcinoma' \
			--cancer-study-identifier dcis_gsi_2019 \
			--name 'Ductal Carcinoma in Situ' \
			--short-name 'dcis' \
			--description 'DCIS Samples sequenced and analyzed at OICR' \
			--key /u/kchandan/cbioportal.pem \
			--push \
			--verbose \
			--force
```
``` 
python3.6m janus.py 	--config ../study_input/DCIS/study.txt \
			--output-folder /.mounts/labs/gsiprojects/gsi/cBioGSI/data/project_TEST/cbio_DCIS/  \
			--key /u/kchandan/cbioportal.pem \
			--push \
			--verbose \
			--force
```
