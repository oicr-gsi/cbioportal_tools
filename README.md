#  CbiOportalWrapper TOol (COW TOwn)
Tools for import of data and administration of the GSI cBioPortal instance. It is dependant on cBioWrap.

This will generate the configuration and prep files for cBioWrap, generate the study using it then import to the cBioPortal instance.

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

_src/_ contains all the Python scripts (as of now).

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