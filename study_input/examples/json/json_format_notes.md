# JSON config format for Janus

## Overview

The production edition of Janus is intended to support two types of output:
1. **Sample**: Single-sample JSON, for creation of CGI report in rShiny
2. **Study**: Directory ready for upload to cBioPortal

## Config requirements

In both cases, the root configuration object has two required sub-objects:
1. `samples`: List of objects, representing samples. Exactly one entry for JSON report; one or more entries for study output. Each sample must have `PATIENT_ID` and `SAMPLE_ID` attributes; it may have others for additional sample metadata, eg. `AGE`, `MEAN_COVERAGE`.
2. `genetic alterations`: List of objects, representing analysis outputs. Corresponds to the `genetic_alteration_type` used by cBioPortal. Must contain an `input_files` object, with one file for each sample. May contain additional entries with metadata for Janus or cBioPortal.

## Function of Janus

Janus will operate as follows:
1. Read JSON config
2. For each sample, read genetic alteration results from the given input files
3. Output the results in appropriate format:
   - JSON for rShiny report
   - Directory of metadata/data files for upload to cBioPortal

