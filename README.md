#  janus
janus is a tool for the import of data and administration of the GSI cBioPortal instance. 

Janus has multiple faces, as of now, just 4. Each one defines a set of functions that are described more accurately [here.](src/README.md)

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

### `janus.py generator`

For each face of janus there is help, however the heaviest face `generator` creates and uploads a study from raw data to your cBioPortal instance.

If you are using the runner script you must simply specify the location of your study configuration files.

Should you be exporting the study to a cBioPortal instance, a log file will be generated of the import process in the study folder.

You will need a minimum of 16g. i.e. `qrsh -l h_vmem=16g`* I recommend having `32g` or more, as more samples can then be processed in parallel.

\* I don't actually know the minimum, but this is the most I've seen used.

#### Minimal Study:

Refer to [Specification README.md](study_input/Specification/README.md#minimal-study)

### `janus.py import`

This face will take either a complete study or a `gene-panel` file and will upload them to a target cBioPortal instance and restart it.

### `janus.py remove`

This face will remove a study from a target instance given a `cancer_study_id`, and will automatically restart the instance.

### `janus.py query`

This face will query an instance for `cancer-type`s and `gene-panel`s. It should grow to query more properties.

## Contributing:

Refer to [`CONTRIBUTING.md`](CONTRIBUTING.md)

Lists all steps that should be taken to ensure proper and complete integration of new feature.


## What's in each folder?

* [`src/`](src) contains all the scripts, with deeper organization as you go

* [`study_input/`](study_input) contains example input configuration files for sample studies.

* [`study_input/Specification/`](study_input/Specification) contains documentation on making your own config files.

* [`src/lib/study_generation/README.md`](src/lib/study_generation/README.md) contains documentation on contributing and expanding `janus.py` functionality.

## Dependencies
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

# Copyright and License

Copyright (C) 2019, 2020 by Genome Sequence Informatics, Ontario Institute for Cancer Research

Licensed under the [https://www.gnu.org/licenses/gpl-3.0.en.html](GPL 3.0 license).
