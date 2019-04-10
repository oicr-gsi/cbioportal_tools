# _src_ folder

Run with `./runner.sh` all arguments can be modified:

To submit a job, run `qsub_Janus.sh` with **your** email.

### Detailed help:

```
usage: janus.py [-h] [-c FILE] -o FOLDER [-t TYPE] [-i ID] [-N NAME] [-n NAME]
                [-d DESCRIPTION] [--sample-info SAMPLE_INFO]
                [--patient-info PATIENT_INFO] [--cancer-type CANCER_TYPE]
                [--timeline-info TIMELINE_INFO]
                [--mutation-data MUTATION_DATA]
                [--segmented-data SEGMENTED_DATA]
                [--expression-data EXPRESSION_DATA]
                [--expression-zscores-data EXPRESSION_ZSCORES_DATA]
                [--log2CNA-data LOG2CNA_DATA] [--CNA-data CNA_DATA]
                [--fusions-data FUSIONS_DATA]
                [--methylation-hm27-data METHYLATION_HM27_DATA]
                [--rppa-data RPPA_DATA]
                [--gistic-genes-amp-data GISTIC_GENES_AMP_DATA]
                [--mutsig-data MUTSIG_DATA]
                [--GENE-PANEL-data GENE_PANEL_DATA]
                [--gsva-scores-data GSVA_SCORES_DATA] [-k FILE] [-p] [-v]

janus (https://github.com/oicr-gsi/cbioportal_tools) is a CLI tool to generate
an importable study for a cBioPortal instance. Recommended usage can be seen
in the examples located in ../study_input/ .

optional arguments:
  -h, --help            show this help message and exit
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
  -k FILE, --key FILE   The RSA key to cBioPortal. Should have appropriate
                        read write restrictions
  -p, --push            Push the generated study to the cBioPortal Instance
  -v, --verbose         Makes program verbose

Overridable Required Configuration File Specifiers:
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
  --timeline-info TIMELINE_INFO
                        Location of timeline-info configuration file: will
                        override TIMELINE specification in the config file.
                        THIS HAS NOT BEEN IMPLEMENTED YETSee the docs OPTIONAL

Overridable Optional Data-type Configuration File Specifiers:
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
  --log2CNA-data LOG2CNA_DATA
                        Location of log2CNA-data configuration file: will
                        override CONTINUOUS_COPY_NUMBER specification in the
                        config file. THIS HAS BEEN IMPLEMENTED PARTIALLY. See
                        the docs OPTIONAL
  --CNA-data CNA_DATA   Location of CNA-data configuration file: will override
                        DISCRETE_COPY_NUMBER specification in the config file.
                        THIS HAS BEEN IMPLEMENTED PARTIALLY. See the docs
                        OPTIONAL
  --fusions-data FUSIONS_DATA
                        Location of fusions-data configuration file: will
                        override FUSION specification in the config file. THIS
                        HAS NOT BEEN IMPLEMENTED YET. See the docs OPTIONAL
  --methylation-hm27-data METHYLATION_HM27_DATA
                        Location of methylation-hm27-data configuration file:
                        will override METHYLATION specification in the config
                        file. THIS HAS NOT BEEN IMPLEMENTED YET. See the docs
                        OPTIONAL
  --rppa-data RPPA_DATA
                        Location of rppa-data configuration file: will
                        override PROTEIN specification in the config file.
                        THIS HAS NOT BEEN IMPLEMENTED YET. See the docs
                        OPTIONAL
  --gistic-genes-amp-data GISTIC_GENES_AMP_DATA
                        Location of gistic-genes-amp-data configuration file:
                        will override GISTIC_2.0 specification in the config
                        file. THIS HAS NOT BEEN IMPLEMENTED YET. See the docs
                        OPTIONAL
  --mutsig-data MUTSIG_DATA
                        Location of mutsig-data configuration file: will
                        override MUTSIG specification in the config file. THIS
                        HAS NOT BEEN IMPLEMENTED YET. See the docs OPTIONAL
  --GENE-PANEL-data GENE_PANEL_DATA
                        Location of GENE-PANEL-data configuration file: will
                        override GENE_PANEL specification in the config file.
                        THIS HAS NOT BEEN IMPLEMENTED YET. See the docs
                        OPTIONAL
  --gsva-scores-data GSVA_SCORES_DATA
                        Location of gsva-scores-data configuration file: will
                        override GENE_SET specification in the config file.
                        THIS HAS NOT BEEN IMPLEMENTED YET. See the docs
                        OPTIONAL
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
