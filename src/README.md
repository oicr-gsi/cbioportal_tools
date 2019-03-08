# _src_ folder

Run with ```./runner.sh``` all arguments can be modified:

### Detailed help:

```
usage: Janus.py [-h] [-o FOLDER] [-c FILE] [-t TYPE] [-i ID] [-N NAME]
                [-n NAME] [-d DESCRIPTION] [-k FILE] [-p] [-v] [-f]

Heyoka (https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to
generate an importable study for a cBioPortal instance.Recommended usage can
be seen in the examples located in study_input/ .

optional arguments:
  -h, --help            show this help message and exit
  -o FOLDER, --output-folder FOLDER
                        The main folder of the study you want to generate.
  -c FILE, --config FILE
                        The location of the study config file.
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
```
### Examples:
```
python3.6 Janus.py \
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
			
or 

python3.6m Janus.py 	--config ../study_input/DCIS/study.txt \
			--output-folder /.mounts/labs/gsiprojects/gsi/cBioGSI/data/project_TEST/cbio_DCIS/  \
			--key /u/kchandan/cbioportal.pem \
			--push \
			--verbose \
			--force
```