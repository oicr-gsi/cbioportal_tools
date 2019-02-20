#!/usr/bin/env bash

# Load required modules
module use /oicr/local/analysis/Modules/modulefiles
module use /.mounts/labs/PDE/Modules/modulefiles
module load vep/92
module load vcf2maf
module load python-gsi/3.6.4

# Run main script:

python3.6m main.py 	--study-info ../study_input/study.txt \
					--study-output-folder /.mounts/labs/gsiprojects/gsi/cBioGSI/data/snv/cbioMutect \
					--push \
					--verbose \
					--force
/