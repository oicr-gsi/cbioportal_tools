#  janus
janus is a tool for the import of data and administration of the GSI cBioPortal instance. 

This will generate meta and data files for cBioPortal, then import to the cBioPortal instance.

More information on the file types from cBioPortal is [Data Loading](https://cbioportal.readthedocs.io/en/latest/Data-Loading.html),
and [File Formats](https://cbioportal.readthedocs.io/en/latest/File-Formats.html). 
We also have links to the OICR Wiki. [cBioPortal Study Components](https://wiki.oicr.on.ca/display/GSI/cBioPortal+Study+Components)
and [cBioPortal-Tools](https://wiki.oicr.on.ca/display/GSI/cBioPortal-Tools)

```
   ______            ______   
  /(@/@@@@\        /@@@@\@)\  
 |(@|@@@@@@\__  __/@@@@@@|@)| 
  \(@\@@@@@@|)\/(|@@@@@@/@)/   
     |    @@@|)(|@@@    |     
     /~     @|@@|@    (~\     
    /_     @@|@@|@@     _\    
      ~    @@@@@@@@    ~      
@     %@@@@@      @@@@@%     @
 @@@@@@@@@ \______/ @@@@@@@@@ 
```

## Usage

Run the importer script with:
```
./runner.sh
```
Within the runner script you must simply specify the location of your study configuration files.

You will need a minimum of 16g. i.e. `qrsh -l h_vmem=16g`*

*I don't actually know the minimum, but this is the most I've seen used.

### What's in each folder?

* [`src/`](src) contains all the scripts, with deeper organization as you go

* [`study_input/`](study_input) contains example input configuration files for sample studies.

* [`study_input/Specification/`](study_input/Specification) contains documentation on making your own input.

* [`src/lib/study_generation/README.md`](src/lib/study_generation/README.md) contains documentation on contributing and expanding `janus.py` functionality.

### Dependencies
You shouldn't need this if you use the runner script.

This tool depends on:

Python libraries required, should be available under:
* `python-gsi/3.6.4`
  * `pandas`
  * `numpy`
  * `argparse`

Linux command line utilities:
* `awk`, `sort`, `uniq`, `grep`

OICR Spec
* `vep/92`
* `vcf2maf`
* `python-gsi/3.6.4`
* `R-gsi/3.5.1`

Python packages require pip however they are included in `python-gsi`, to install/load everything on OICR nodes, run:

Both `module use ...` statements are required.
```
module use /oicr/local/analysis/Modules/modulefiles
module use /.mounts/labs/PDE/Modules/modulefiles
module load vep/92
module load vcf2maf
module load python-gsi/3.6.4
module load R-gsi/3.5.1
```