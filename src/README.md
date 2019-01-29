# src folder
This folder contains most scripts. 
The test folder within has any scripts used in testing and validation.
## Usage - generate_bare_data_samples.py
Run the generate_bare_data_samples.py program with:

```
positional arguments:
  input_folder          The input folder can contain compressed: [.tar.gz |
                        .gz | .zip] or uncompressed format in: [vcf | maf]

optional arguments:
  -h, --help            show this help message and exit
  -i, --study-id        This is the cancer study ID, a unique string. This
                        will soon be managed another way
  -s, --study_folder    The folder you want to export this generated
                        data_samples.txt file to. Generally this will be the
                        main folder of the study being generated. If left
                        blank this will generate it wherever you run the
                        script from.
```

For example:

```
python generate_bare_data_samples.py -h
or
python generate_bare_data_samples.py ../GATKHaplotypeCaller/ brca_gsi_2019
or
python generate_bare_data_samples.py Mutect2/ kremen1_octane -s new_study/ 
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