# src folder
The _main_minimal.py_ script essentially combines the main scripts of the generate_study_meta and generate_data_meta_samples into one easy to understand script. All arguments are mandatory.


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
                        be used alongside -c. If you do -c takes precedence.
  -c , --cli            Command Line Input, the description, name, short_name
                        and type_of_cancer in semi-colon separated values.
                        Input needs to be wrapped with ''.e.g. -c 'GECCO
                        Samples sequenced and analyzed at OICR;Genetics and
                        Epidemiology of Colorectal Cancer
                        Consortium;GECCO;colorectal'
  -v, --verbose         Makes program verbose

Required Arguments:
  -i , --study-input-folder 
                        The input folder can contain compressed: [.tar.gz |
                        .gz | .zip] or uncompressed format in: [vcf | maf]
  -s , --study-id       This is the cancer study ID, a unique string. Please
                        use the format gene_lab_year. e.g.brca_gsi_2019 or
                        mixed_tgl_2020
  -o , --study-output-folder 
                        The folder you want to export this generated
                        data_samples.txt file to. Generally this will be the
                        main folder of the study being generated. If left
                        blank this will generate it wherever you run the
                        script from.
```

For example:

```
python generate_study_meta.py -h
or
python main_minimal.py -i test/fakes/ -o new_study/ -s gecco_gsi_2019 -c 'GECCO Samples sequenced and analyzed at OICR;Genetics and Epidemiology of Colorectal Cancer Consortium;GECCO;colorectal' -v
```
___
___

\*\*
**Using any of these scripts below individually is not recommended, and can lead to a malformed study. However documentation is still there if you're feeling lucky.**
___
___
## Usage - generate_study_meta.py
Run the generate_study_meta.py program with:

```
optional arguments:
  -h, --help            show this help message and exit
  -d, --default         Prevents need for user input by trying to parse study
                        ID, you must follow format indicated in the help if
                        you use this. **This tag is not recommended and cannot
                        be used alongside -c. If you do -c takes precedence.
  -c , --cli            Command Line Input, the description, name, short_name
                        and type_of_cancer in semi-colon separated values.
                        Input needs to be wrapped with ''.e.g. -c 'GECCO
                        Samples sequenced and analyzed at OICR;Genetics and
                        Epidemiology of Colorectal Cancer
                        Consortium;GECCO;colorectal'
  -v, --verbose         Makes program verbose

Required Arguments:
  -s , --study-id       This is the cancer study ID, a unique string. Please
                        use the format gene_lab_year. e.g.brca_gsi_2019 or
                        mixed_tgl_2020
  -o , --study-output-folder 
                        The folder you want to export this generated
                        data_samples.txt file to. Generally this will be the
                        main folder of the study being generated. If left
                        blank this will generate it wherever you run the
                        script from.
```

For example:

```
python generate_study_meta.py -h
or
python generate_study_meta.py -i brca_gsi_2019 -f new_study_2019/ -t brca
or
python generate_study_meta.py -i cbl_tgl_2000 -f new_study_2000/ -t bcl -d
```
## Usage - generate_data_meta_samples.py
Run the generate_data_meta_samples.py program with:

```
optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Makes program verbose

Required Arguments:
  -i , --study-input-folder 
                        The input folder can contain compressed: [.tar.gz |
                        .gz | .zip] or uncompressed format in: [vcf | maf]
  -s , --study-id       This is the cancer study ID, a unique string. Please
                        use the format gene_lab_year. e.g.brca_gsi_2019 or
                        mixed_tgl_2020
  -o , --study-output-folder   
  						The folder you want to export this generated
                        data_samples.txt file to. Generally this will be the
                        main folder of the study being generated. If left
                        blank this will generate it wherever you run the
                        script from.
```

For example:

```
python generate_data_meta_samples.py -h
or
python generate_data_meta_samples.py test/fakes/ -i brca_gsi_2019 -s new_study/
or
python generate_data_meta_samples.py Mutect2/ kremen1_octane -s new_study/ 
```
## Usage - import_mutation_data.py
Run the import_mutation_data.py program with:

```
positional arguments:
  inputFile             The input file, can be of compressed: .tar.gz | .gz |
                        .zip] or uncompressed format in: [vcf | maf] If the
                        file is compressed, optional tag -c must be added

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -c, --compressed      If the input file is compressed this tag must be added
  -w, --workflowUsed    The workflow used is a mandatory tag, choices are:
                        [GATKHaplotypeCaller | Mutect | Mutect2 | Strelka]
```

For example:

```
python import_mutation_data.py -h
or
python import_mutation_data.py banana.vcf.tar.gz -c -w Mutect
or
python import_mutation_data.py apple.maf -w GATKHaplotypeCaller
```