CHANGELOG
=========

## Unreleased
### Added
- GRD-251: Simple unit tests for generator mode
- GRD-252:
  - Generator test for CAP expression data
  - `test.py` with all tests; `fast_test.py` with a subset of tests
### Changed
- GRD-254: Remove unnecessary metadata attributes; add docstrings
- GRD-259: Change module structure to better reflect the application hierarchy
- GRD-264: Eliminate filesystem warnings in tests
- GRD-627: New class structure for generator
  - Data is written by _components_ defined in `components.py`
  - New configuration format defined in `generate/config.py` and `utilities/config.py`
  - Additional utility code in `utilities`
  - Encapsulate legacy pipelines in `legacy_pipeline_component` class; can run with minimal changes
  - Working test in `new_test.py`
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

## v0.0.1: 2020-07-03
- Initial development release
- Corresponds to version 0.0.1 in [Modulator](https://gitlab.oicr.on.ca/ResearchIT/modulator/-/blob/master/code/gsi/70_janus.yaml)
- Package is released as-is; significant bugs and issues remain
