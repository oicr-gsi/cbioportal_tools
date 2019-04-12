# _src_ folder

Run with `./runner.sh` all arguments can be modified:

To submit a job, run `qsub_Janus.sh` with **your** email.

### Detailed help:

```
usage: janus.py [-h] [-c FILE] -o FOLDER [-t TYPE] [-i ID] [-N NAME] [-n NAME]
                [-d DESCRIPTION] --path PATH [--sample-info SAMPLE_INFO]
                [--patient-info PATIENT_INFO] [--cancer-type CANCER_TYPE]
                [--mutation-data MUTATION_DATA]
                [--segmented-data SEGMENTED_DATA]
                [--continuous-data CONTINUOUS_DATA]
                [--discrete-data DISCRETE_DATA]
                [--expression-data EXPRESSION_DATA]
                [--expression-zscores-data EXPRESSION_ZSCORES_DATA]
                [--fusion-data UNSUPPORTED] [--methylation-data UNSUPPORTED]
                [--protein-data UNSUPPORTED] [--timeline-info UNSUPPORTED]
                [--gistic2-data UNSUPPORTED] [--mutsig-data UNSUPPORTED]
                [--gene-panel-data UNSUPPORTED] [--gene-set-data UNSUPPORTED]
                [--custom-case-list UNSUPPORTED] [-k FILE] [-p] [-u URL] [-v]

janus (https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate
an importable study for a cBioPortal instance. Recommended usage can be seen
in the examples located in ../study_input/ .

optional arguments:
  -h, --help            show this help message and exit
  -k FILE, --key FILE   The RSA key to cBioPortal. Should have appropriate
                        read write restrictions
  -p, --push            Push the generated study to the cBioPortal Instance
  -u URL, --url URL     Override the url for cBioPortal instance DO NOT
                        include https
  -v, --verbose         Makes program verbose

Study Arguments (Required)::
  -c FILE, --config FILE
                        The location of the study config file, in essence a
                        set of command-line arguments. Recommended usage is
                        with configuration file. File data can be overridden
                        by command-line arguments.
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
  --path PATH           Path of Janus.py

Overridable Required Configuration File Specifiers::
  --sample-info SAMPLE_INFO
                        Location of sample-info configuration file: will
                        override SAMPLE_ATTRIBUTES specification in the config
                        file. REQUIRED.
  --patient-info PATIENT_INFO
                        Location of patient-info configuration file: will
                        override PATIENT_ATTRIBUTES specification in the
                        config file. REQUIRED.
  --cancer-type CANCER_TYPE
                        Location of cancer-type configuration file: will
                        override CANCER_TYPE specification in the config file.
                        REQUIRED*
  --timeline-info UNSUPPORTED
                        Location of timeline-info configuration file: will
                        override TIMELINE specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED

Overridable Optional Data-type Configuration File Specifiers::
  --mutation-data MUTATION_DATA
                        Location of mutation-data configuration file: will
                        override MAF specification in the config file.
                        OPTIONAL
  --segmented-data SEGMENTED_DATA
                        Location of segmented-data configuration file: will
                        override SEG specification in the config file. The
                        segmented data file will normally generate _CNA and
                        _log2CNA files. See documentation if you do not want
                        this. OPTIONAL
  --continuous-data CONTINUOUS_DATA
                        Location of continuous-data configuration file: will
                        override CONTINUOUS_COPY_NUMBER specification in the
                        config file.See the docs. OPTIONAL
  --discrete-data DISCRETE_DATA
                        Location of discrete-data configuration file: will
                        override DISCRETE_COPY_NUMBER specification in the
                        config file. See the docs. OPTIONAL
  --expression-data EXPRESSION_DATA
                        Location of expression-data configuration file: will
                        override MRNA_EXPRESSION specification in the config
                        file. files. See the documentation if you do not want
                        this. OPTIONAL
  --expression-zscores-data EXPRESSION_ZSCORES_DATA
                        Location of expression-zscores-data configuration
                        file: will override MRNA_EXPRESSION_ZSCORES
                        specification in the config file. files. See the
                        documentation if you do not want this. OPTIONAL
  --fusion-data UNSUPPORTED
                        Location of fusion-data configuration file: will
                        override FUSION specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --methylation-data UNSUPPORTED
                        Location of methylation-data configuration file: will
                        override METHYLATION specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --protein-data UNSUPPORTED
                        Location of protein-data configuration file: will
                        override PROTEIN specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --gistic2-data UNSUPPORTED
                        Location of gistic2-data configuration file: will
                        override GISTIC2 specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --mutsig-data UNSUPPORTED
                        Location of mutsig-data configuration file: will
                        override MUTSIG specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --gene-panel-data UNSUPPORTED
                        Location of gene-panel-data configuration file: will
                        override GENE_PANEL specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --gene-set-data UNSUPPORTED
                        Location of gene-set-data configuration file: will
                        override GENE_SET specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED
  --custom-case-list UNSUPPORTED
                        Location of custom-case-list configuration file: will
                        override CASE_LIST specification in the config file.
                        UNSUPPORTED. See the docs. OPTIONAL -- UNSUPPORTED

```
### Examples:
```
python3 janus.py \
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
```
``` 
python3 janus.py 	--config ../study_input/DCIS/study.txt \
			--output-folder /.mounts/labs/gsiprojects/gsi/cBioGSI/data/project_TEST/cbio_DCIS/  \
			--key /u/kchandan/cbioportal.pem \
			--push \
			--verbose \
```
