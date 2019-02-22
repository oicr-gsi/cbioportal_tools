# _src_ folder
Run with ```./runner.sh``` all arguments can be modified:

```
--study-info ../Location_of_/study.txt
# Location of the study config file

--study-output-folder /path/to/output
# Location of output

--key /whatever/key.pem
# The key to ssh into the running instance of cBioPortal

--push
# Pushes the study to the instance

--verbose
# Prints verbose, for debugging
```

###Detailed help:

```
usage: main.py [-h] [-o FOLDER] [-s FILE] [-k FILE] [-p] [-v] [-f]

cBioPortal-Tools (https://github.com/oicr-gsi/cbioportal_tools) is a command
line tool for extracting data from files generated through the seqware
workflows, as well as from tools run outside of the pipeline, and put them
into the correct cBioPortal import files
(https://cbioportal.readthedocs.io/en/latest/File-Formats.html).

optional arguments:
  -h, --help            show this help message and exit
  -p, --push            Push the generated study to the cBioPortal Instance
  -v, --verbose         Makes program verbose
  -f, --force           Forces overwriting of data_cancer_type.txt file and
                        *.maf files.

Required Arguments:
  -o FOLDER, --study-output-folder FOLDER
                        The main folder of the study you want to generate.
  -s FILE, --study-info FILE
                        The location of the study input information
  -k FILE, --key FILE   The RSA key to cBioPortal. Should have appropriate
                        read write restrictions

```