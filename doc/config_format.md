# Configuration files in Janus

## Overview

Configuration for Janus report generation (version 0.0.2 and up) is in the [CSVY](http://csvy.org) format. CSVY consists of an optional header in [YAML](https://yaml.org/) format, followed by TSV data in the document body.

CSVY is not a very widespread format, although it is in use for other projects at OICR-GSI and there is a [csvy module in R](https://cran.r-project.org/web/packages/csvy/index.html) to read and write it.

Usage of YAML in Janus allows consistency with the YAML-like metadata format used by cBioPortal.

Janus has its own CSVY parser, written in Python. It uses the [PyYAML](https://pypi.org/project/PyYAML/) and [pandas](https://pandas.pydata.org/) packages to parse YAML and tabular data, respectively.

## Brief description of CSVY

See the [CSVY](http://csvy.org) homepage for a full specification. In brief, the format implemented in Janus is as follows:

- The YAML header is optional.
- If present, the header must begin and end with the line `---` or `...`.
- Each line between the start and end of the header must begin with a `#`.
- After the initial `#` from each line is removed, the header must be valid YAML.
- The first line of the TSV body contains column headers.
- The second and subsequent lines of the TSV body contain data fields.
- Lines in the TSV body which begin with `#` are interpreted as comments and ignored.

## Schema for Janus config files

The content of a Janus config file may be defined by a _schema_.

A schema allows us to:
- Validate that a config file is in the correct format
- Write a template to use for creating a new config file

See [schema.md](./doc/schema.md) for details.
