# cBioPortal_Tools
Tools for import of data and administration of the GSI cBioPortal instance

Currently working on converting _.vcf_ -> _.maf_ -> Mutation Data

## Usage
Run the program with:

```
positional arguments:
  inputFile             The input file, can be of compressed: .tar.gz | .gz |
                        .zip] or uncompressed format in: [vcf | maf] If the
                        file is compressed, optional tag -c must be added

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -c, --compressed      If the input file is compressed this tag must be added
  -w , --workflowUsed   The workflow used is a mandatory tag, choices are:
                        [GATKHaplotypeCaller | Mutect | Mutect2 | Strelka]
```

For example:

```
python main.py -h
```
or
```
python main.py banana.vcf.tar.gz -c -w Mutect
```
or
```
python main.py apple.maf -w GATKHaplotypeCaller
```