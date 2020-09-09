CHANGELOG
=========

## v0.0.4: 2020-09-09
### Added
- GRD-273: Enabled and added tests for:
  - `MUTATION_EXTENDED/CAP_CNA.py`
  - `MRNA_EXPRESSION/Cufflinks.py`
- GRD-279: Validate and generate templates for config files
  - Schema class added, with tests
  - Documentation in [/doc/schema.md](./doc/schema.md).
### Changed
- GRD-284: Install and read accessory files
  - R scripts and data files are now installed by `setup.py`
  - Data files for legacy pipeline scripts default to source tree versions; some can be overridden in config
  - Clean up execution of `seg2gene.r`
  - Refactoring and test for main `janus.py` script
- GRD-284: If FASTA reference is not in config file, try to find from environment module
- GRD-284: Refactor `decompress_to_temp` method
  - Rename to `relocate_inputs`; eliminate system calls; make config update explicit; add test
- GRD-284: Refactor `concat_files` method and add test
### Removed
- Unused Python files:
  - `src/lib/generate/analysis_pipelines/cancer_type.py`
  - `src/lib/generate/analysis_pipelines/MRNA_EXPRESSION/mrna_zscores_data.py`
  - `src/lib/support/cbioportal_interface.py`
- Unused R script `src/lib/generate/analysis_pipelines/MRNA_EXPRESSION/get_tcga.r`
- Obsolete copy of `cancer_colours.csv`
- Obsolete README files
- Unnecessary wrappers for `subprocess` functions in `helper.py`

## v0.0.3: 2020-08-10
### Added
- GRD-273: Add support for legacy pipelines
- GRD-273: Enabled and added tests for:
  - `MUTATION_EXTENDED/CAP_mutation.py`
  - `MUTATION_EXTENDED/Mutect.py`
  - `MUTATION_EXTENDED/Mutect2.py`
  - `MUTATION_EXTENDED/MutectStrelka.py`
  - `MUTATION_EXTENDED/Strelka.py`
- GRD-273: Script updated, but *not* enabled or tested
  - `MUTATION_EXTENDED/GATKHaplotypeCaller.py`
- GRD-275:
  - Install data files in `setup.py`
  - Add `__init__.py` files to enabled analysis pipeline directories; ensures they are installed by `setup.py`
### Changed
  - Check that legacy scripts compile in dry-run mode
### Removed
  - Unused script `MUTATION_EXTENDED/MAF.py`
### Fixed
- Add colour designation to `cancer_type` component; present in v0.0.1, inadvertently dropped in v0.0.2
- Generate metadata in mutation scripts other than `CAP_mutation.py`; missing in v.0.0.1
- Remove hard-coded home directory path for `vep_keep_columns.txt`; instead read from the `generate/data` directory

## v0.0.2: 2020-07-30
### Summary
- Development release with extensive refactoring
- Proof-of-concept for new class structure; see GRD-267
- Tests and runs the `CAP_expression` pipeline only; other analysis pipelines TBD
- Removes the untested `query`, `remove`, and `upload/import` modes; only `generator` remains
### Added
- GRD-251: Simple unit tests for generator mode
- GRD-252: Generator test for CAP expression data
- GRD-274: `setup.py` script for installation
### Changed
- GRD-254: Remove unnecessary metadata attributes; add docstrings
- GRD-259: Change module structure to better reflect the application hierarchy
- GRD-264: Eliminate filesystem warnings in tests
- GRD-267: New class structure for generator
  - Data is written by _components_ defined in `components.py`
  - New configuration format defined in `generate/config.py` and `utilities/config.py`
  - Additional utility code in `utilities`
  - Encapsulate legacy pipelines in `legacy_pipeline_component` class; can run with minimal changes
  - Working test in `test.py` (previously `new_test.py`)
### Removed
- GRD-253: Remove `--path` argument to `generator.py`
- GRD-261: Delete the `remove_data_type` directory
- GRD-271:
  - Removed obsolete generator code
  - Replaced legacy generation of default study lists
- GRD-272:
  - Calls to old classes/modules
  - Self-contained push to cBioPortal instance from `generator.py`. For now can be accomplished by separate push script; may reinstate later.
  - Code to override config file options on the command line; may reinstate later.
  - `resolve_priority_queue` method. Reinstate later if needed; see [GitHub issue](https://github.com/oicr-gsi/cbioportal_tools/issues/80).
- GRD-276:
  - Remove the `upload/import`, `query`, and `remove` top-level tools; may reinstate later
  - Remove convenience scripts `qsub_Janus.sh` and `runner.sh`

## v0.0.1: 2020-07-03
- Initial development release
- Corresponds to version 0.0.1 in [Modulator](https://gitlab.oicr.on.ca/ResearchIT/modulator/-/blob/master/code/gsi/70_janus.yaml)
- Package is released as-is; significant bugs and issues remain
