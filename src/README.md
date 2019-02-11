# src folder
The _main_minimal.py_ script essentially combines the main scripts of the generate_study_meta and generate_data_meta_samples into one easy to understand script. All arguments are mandatory.

* _helper.py_ is a script that contains some of the shared functions of many files
* All scripts starting with _generate\_..._ create their respective files specified by the _meta_ or _data_ files and the type.


This folder contains most scripts. 
The test folder within has any scripts used in testing and validation.

# Usage - main_minimal.py
Run the main_minimal.py program with:

```
optional arguments:
  -h, --help            show this help message and exit
  -d, --default         Prevents need for user input by trying to parse study
                        ID, you must follow format indicated in the help if
                        you use this. **This tag is not recommended and cannot
                        be used alongside -c as -c takes precedence.
  -v, --verbose         Makes program verbose
  -f, --force           Forces overwriting of data_cancer_type.txt file and
                        *.maf files.

Required Arguments:
  -i FOLDER, --study-input-folder FOLDER
                        The input folder can contain compressed: [.tar.gz |
                        .gz | .zip] or uncompressed format in: [vcf | maf]
  -o FOLDER, --study-output-folder FOLDER
                        The folder you want to export this generated
                        data_samples.txt file to. Generally this will be the
                        main folder of the study being generated. If left
                        blank this will generate it wherever you run the
                        script from.
  -s STRING, --study-id STRING
                        This is the cancer study ID, a unique string. Please
                        use the format gene_lab_year. e.g.brca_gsi_2019 or
                        mixed_tgl_2020
  -c STRING, --cli-study STRING
                        Command Line Input, the description, name, short_name
                        and type_of_cancer in semi-colon separated values.
                        Input needs to be wrapped with ''.e.g. -c 'GECCO
                        Samples sequenced and analyzed at OICR;Genetics and
                        Epidemiology of Colorectal Cancer
                        Consortium;GECCO;colorectal'
  -C CALLER_NAME, --caller CALLER_NAME
                        The caller from which the mutation data is being
                        created from. Choices: [GATKHaplotype | Mutect |
                        Mutect2 | Strelka | MutectStrelka]
  -l STRING, --cli-case-list STRING
                        Command Line Input, case_list_name and
                        case_list_description in semi-colon separated values.
                        Input needs to be wrapped with ''.e.g. -c 'All
                        Tumours;All tumor samples (over 9000 samples)'
  -k FILE, --cbioportal-key FILE
                        The RSA key to cBioPortal. Should have appropriate
                        read write restrictions
```

For example:

```
python3.6m generate_study_meta.py -h
or
python3.6m main_minimal.py \
-i /.mounts/labs/gsiprojects/gsi/cBioGSI/data/snv/Strelka \
-o /.mounts/labs/gsiprojects/gsi/cBioGSI/data/snv/cbioStrelka \
-s gecco_gsiMore_2019 \
-c 'GECCO Samples sequenced and analyzed at OICR;Genetics and Epidemiology of Colorectal Cancer Consortium;GECCO;colorectal' \
-C Strelka \
-l 'All Tumours;All tumor samples (over 9000 samples)' \
-v -f
```
___
___

\*\*
**Using any of these scripts below individually is not recommended, and can lead to a malformed study. However documentation is still there if you're feeling lucky.**
___
___
## Usage - generate_meta_study.py
Run the generate_meta_study.py program with:

```
optional arguments:
  -h, --help            show this help message and exit
  -d, --default         Prevents need for user input by trying to parse study
                        ID, you must follow format indicated in the help if
                        you use this. **This tag is not recommended and cannot
                        be used alongside -c. If you do -c takes precedence.
  -v, --verbose         Makes program verbose

Required Arguments:
  -s STRING, --study-id STRING
                        This is the cancer study ID, a unique string. Please
                        use the format gene_lab_year. e.g.brca_gsi_2019 or
                        mixed_tgl_2020
  -c STRING, --cli-study STRING
                        Command Line Input, the description, name, short_name
                        and type_of_cancer in semi-colon separated values.
                        Input needs to be wrapped with ''.e.g. -c 'GECCO
                        Samples sequenced and analyzed at OICR;Genetics and
                        Epidemiology of Colorectal Cancer
                        Consortium;GECCO;colorectal'
```

For example:

```
python3 generate_meta_study.py -h
or
python3 generate_meta_study.py -s brca_gsi_2019 -c 'Descriptive description;Name of Study;Short Name;type_of_cancer'
or
python3 generate_meta_study.py -s cbl_tgl_2000 -c 'Descriptive description;Name of Study;Short Name;type_of_cancer'
```
## Usage - generate_data_meta_samples.py
Run the generate_data_meta_samples.py program with:

```
optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Makes program verbose

Required Arguments:
  -i FOLDER, --study-input-folder FOLDER
                        The input folder can contain compressed: [.tar.gz |
                        .gz | .zip] or uncompressed format in: [vcf | maf]
  -o FOLDER, --study-output-folder FOLDER
                        The folder you want to export this generated
                        data_samples.txt file to. Generally this will be the
                        main folder of the study being generated. If left
                        blank this will generate it wherever you run the
                        script from.
  -s STRING, --study-id STRING
                        This is the cancer study ID, a unique string. Please
                        use the format gene_lab_year. e.g.brca_gsi_2019 or
                        mixed_tgl_2020
```

For example:

```
python3 generate_data_meta_samples.py -h
or
python3 generate_data_meta_samples.py -i test/fakes/ -s brca_gsi_2019 -o new_study/
or
python3 generate_data_meta_samples.py -i Mutect2/ -s kremen1_octane_2020 -o new_study/ 
```