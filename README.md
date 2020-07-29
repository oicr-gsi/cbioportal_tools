#  Janus

## Overview

Janus provides a gateway to a [cBioPortal](https://www.cbioportal.org/) instance. It is named for the Roman god of doorways and transitions.

Janus takes as its input pipeline data and metadata, as generated at the [Ontario Institute for Cancer Research](https://oicr.on.ca/). Its core (and for now, only) function is to prepare a study directory for upload, as specified in the [cBioPortal documentation](https://docs.cbioportal.org/5.1-data-loading/data-loading/file-formats).

This document provides a general introduction to Janus. Further documentation is in the `doc` subdirectory. Janus has a changelog in `CHANGELOG.md`.

## Prerequisites

Janus is primarily implemented in Python, with a few ancillary scripts in R. Requirements:

- Python >= 3.7
- Python packages:
  - numpy >= 1.19.0
  - pandas >= 1.0.5
  - PyYAML >= 5.3.1
- R >= 3.5.1
- [ensembl-vep](https://github.com/Ensembl/ensembl-vep) >= 98.0
- [vcf2maf](https://github.com/mskcc/vcf2maf) >= 1.6.17
- Some legacy pipeline scripts require Linux utilities such as `awk` and `grep`
- Minimum 16G of RAM (32G is preferred)

## Installation and Testing

Janus has a `setup.py` script and can be installed using [pip](https://pypi.org/project/pip/):
```
pip install $JANUS_SOURCE_DIR
```

Alternatively, to install to a specific directory:
```
pip install --prefix $INSTALL_ROOT $JANUS_SOURCE_DIR
```

To run tests, assuming all prerequisites are installed:
```
export PYTHONPATH=${JANUS_SOURCE_DIR}/src/lib:$PYTHONPATH
./src/test/test.py
```

Example study input appears in the `study_input` subdirectory.

## Usage

The main script is `janus.py`, which is copied to the `bin` subdirectory of the installation. Run `janus.py --help` for usage information.

## Code Structure

The prototype version of Janus in release 0.0.1 required modification to be ready for production. Deprecated code retained from the prototype is referred to as "legacy".

Python modules in `src/lib`:
- `constants`: Legacy constants
- `generate`: Code to generate study directories, ready for upload.
- `generate/analysis_pipelines`: Generation code specific to analysis pipelines. Includes scripts from the legacy version.
- `support`: Legacy support and utility functions
- `utilities`: General purpose code for logging and configuration

## Potential Extension

Janus may later be extended to:
- Upload the study to a cBioPortal instance
- Query a cBioPortal instance
- Delete data from a cBioPortal instance
- Prepare and upload data to resources other than cBioPortal

## Credits

Janus prototype developed by OICR co-op students [Kunal Chandan](https://github.com/kunalchandan) and [Allan Liang](https://github.com/a33liang).

Subsequent development by Iain Bancarz, <ibancarz@oicr.on.ca>.

## Copyright and License

Copyright (C) 2019, 2020 by Genome Sequence Informatics, Ontario Institute for Cancer Research

Licensed under the [GPL 3.0 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
