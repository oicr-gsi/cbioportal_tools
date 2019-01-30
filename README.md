# cBioPortal_Tools
Tools for import of data and administration of the GSI cBioPortal instance

import_mutation_data.py converts from _.vcf_ -> _.maf_. 
This takes compressed _.vcf_ or _.maf_ files to usable _.maf_ files.

More information on the file types from cBioPortal is [Data Loading](https://cbioportal.readthedocs.io/en/latest/Data-Loading.html),
and [File Formats](https://cbioportal.readthedocs.io/en/latest/File-Formats.html). 
We also have links to the OICR Wiki. [cBioPortal Study Components](https://wiki.oicr.on.ca/display/GSI/cBioPortal+Study+Components)
and [cBioPortal-Tools](https://wiki.oicr.on.ca/display/GSI/cBioPortal-Tools)

### What's in each folder?
_template_study_files_ contains a folder of template files that could theoretically be used.
The only difficulty is actually finding all that data you would need to fill each file.

_src/_ contains all the Python scripts (as of now).

_src/test/_ contains testing scripts used for validation

_src/test/fakes_ contains a fake set of files used for testing. Some of them could be generated or taken from sample data.

### Dependencies
This tool depends on:
* pandas
* numpy

These both require pip, to install everything mentioned, run:
```
sudo apt install python-pip

pip install numpy pandas
```