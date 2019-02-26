# CBIoportal_Tools (CuBIT)
Tools for import of data and administration of the GSI cBioPortal instance.

In the current minimal state, the **_main_minimal.py_** script can import the bare minimum for a study. Features will be added as they are developed.

More information on the file types from cBioPortal is [Data Loading](https://cbioportal.readthedocs.io/en/latest/Data-Loading.html),
and [File Formats](https://cbioportal.readthedocs.io/en/latest/File-Formats.html). 
We also have links to the OICR Wiki. [cBioPortal Study Components](https://wiki.oicr.on.ca/display/GSI/cBioPortal+Study+Components)
and [cBioPortal-Tools](https://wiki.oicr.on.ca/display/GSI/cBioPortal-Tools)

## Usage

Run the importer script with:
```
./runner.sh
```
Within the runner script you must specify the location of your study configuration files.


### What's in each folder?
_template_study_files_ contains a folder of template files that could theoretically be used.
The only difficulty is actually finding all that data you would need to fill each file.

_src/_ contains all the Python scripts (as of now).

_src/test/_ contains testing scripts used for validation

_study_input/_ contains the required input configuration files for generating a study.

### Dependencies
This tool depends on:
* pandas
* numpy

These both require pip, to install everything mentioned, run:
```
sudo apt install python3-pip

pip3 install numpy pandas
```