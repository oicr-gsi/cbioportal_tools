# _src_ folder

Run with `./runner.sh` all arguments can be modified:

To submit a job, run `qsub_Janus.sh` with **your** email.

## Detailed help:

```
>>> python3 janus.py -h

usage: janus.py [-h] {generator,import,remove,query} ...

janus.py a set of cBioPortal interaction tools. Janus is a wrapper-like
utility for managing cBioPortal studies and your instance, each sub-tool
functions on it's own. For more usage, examples and documentation see
https://github.com/oicr-gsi/cbioportal_tools

optional arguments:
  -h, --help            show this help message and exit

Janus a set of cBioPortal Tools:
  Current set of tools

  {generator,import,remove,query}
    generator           Generator Functions for generating whole studies from
                        data pipelines. Will require configuration of study
                        configuration files
    import              Importer for complete studies or gene_panels. Requires
                        a cBioPortal ready study or a complete gene_panel
    remove              Removal tool for studies. Requires study_id of
                        particular study
    query               Query tool for gene_panels and cancer_type. Requires
                        password to root MySQL user
```
## Generator
```
>>> python3 janus.py generator -h

usage: janus.py generator [-h] [-c FILE] -o FOLDER [-t TYPE] [-i ID] [-N NAME]
                          [-n NAME] [-d DESCRIPTION] --path PATH
                          [--sample-info SAMPLE_INFO]
                          [--patient-info PATIENT_INFO]
                          [--cancer-type CANCER_TYPE]
                          [--mutation-data MUTATION_DATA]
                          [--segmented-data SEGMENTED_DATA]
                          [--continuous-data CONTINUOUS_DATA]
                          [--discrete-data DISCRETE_DATA]
                          [--expression-data EXPRESSION_DATA]
                          [--fusion-data UNSUPPORTED]
                          [--methylation-data UNSUPPORTED]
                          [--protein-data UNSUPPORTED]
                          [--timeline-info UNSUPPORTED]
                          [--gistic2-data UNSUPPORTED]
                          [--mutsig-data UNSUPPORTED]
                          [--gene-panel-data UNSUPPORTED]
                          [--gene-set-data UNSUPPORTED]
                          [--custom-case-list UNSUPPORTED] [-P [TYPE]]
                          [-k FILE] [-p] [-u URL] [-v]

optional arguments:
  -h, --help            show this help message and exit

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

Pipelines:
  Pipelines printing

  -P [TYPE], --pipelines [TYPE]
                        Query which pipelines are supported and exit. Types
                        are: dict_keys(['MAF', 'SEG', 'MRNA_EXPRESSION',
                        'MRNA_EXPRESSION_ZSCORES', 'CONTINUOUS_COPY_NUMBER',
                        'DISCRETE_COPY_NUMBER'])

Other Supporting Optional Arguments::
  -k FILE, --key FILE   The RSA key to cBioPortal. Should have appropriate
                        read write restrictions
  -p, --push            Push the generated study to the cBioPortal Instance
  -u URL, --url URL     Override the url for cBioPortal instance DO NOT
                        include https
  -v, --verbose         Makes program verbose

```

## Import

```
>>> python3 janus.py import -h

usage: janus.py import [-h] [-f FOLDER] [-g PANEL] -u URL [-k KEY]

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The location of the study folder.
  -g PANEL, --gene-panel PANEL
                        A formatted gene-panel you would like to upload.
  -u URL, --url URL     The location of the cBioPortal instance (address).
  -k KEY, --key KEY     The location of the cBioPortal Key.
```

## Remove

```
>>> python3 janus.py remove -h

usage: janus.py remove [-h] [-i ID] [-u URL] [-k KEY]

optional arguments:
  -h, --help         show this help message and exit
  -i ID, --id ID     The cancer study ID.
  -u URL, --url URL  The location of the cBioPortal instance (address).
  -k KEY, --key KEY  The location of the cBioPortal Key.

```

## Query

```
>>> python3 janus.py query -h

usage: janus.py query [-h] [-u URL] [-p PASSWORD] [-k KEY] [-t] [-g] [-b]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     The location of the cBioPortal instance (address).
  -p PASSWORD, --password PASSWORD
                        mySQL Password.
  -k KEY, --key KEY     The location of the cBioPortal Key.
  -t, --type-of-cancer  Query the types of cancer in the cBioPortal Database
  -g, --gene-panel
                        Query the gene-panels in the cBioPortal Database
  -b, --border          Disables borders around the query.

```

### Examples:
Generating and importing a sample study, while overriding some values in a configuration file:
```
python3 janus.py generator \
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
Generating and importing a sample study:
```
python3 janus.py generator \
			--config ../study_input/DCIS/study.txt \
			--output-folder /.mounts/labs/gsiprojects/gsi/cBioGSI/data/project_TEST/cbio_DCIS/  \
			--key /u/kchandan/cbioportal.pem \
			--push \
			--verbose \
```
Querying the supported pipelines for study generation:
```
python3 janus.py generator -P SEG
```
Importing a gene-panel and a cBioPortal ready study:
```
python3 src/janus.py import 	--url cbioportal-stage.gsi.oicr.on.ca \
				--key /u/kchandan \
				--folder /home/debian/Documents/output/ \
				--gene-panel ../../genepanel.txt \
```
Removing a study by the `study_id: gsi_gecco_2019`:
```
python3 src/janus.py remove 	--id gsi_gecco_2019 \
				--url cboportal.gsi.oicr.on.ca \
```
Querying the cBioPortal database for `gene-panels` and `type-of-cancer`
```
python3 src/janus.py query 	--url cbioportal.gsi.oicr.on.ca \
				--password VERY_SECURE_PASSWORD123 \
				--gene-panel \
				--type-of-cancer \
```