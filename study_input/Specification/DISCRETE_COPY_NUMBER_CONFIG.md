# DISCRETE COPY NUMBER Config
This is the specification for the `DISCRETE_COPY_NUMBER` study config file.

This file may follow the [standard format](STUDY_CONFIG.md).

### Configuring your data

You need to generate the discrete copy number data from the [CONTINUOUS_COPY_NUMBER_CONFIG.txt](CONTINUOUS_COPY_NUMBER_CONFIG.md) pipeline to use the `SEG` pipeline. The definition for the `FILE` pipeline still needs to be figured out.

### Configuring your header

The minimal header will look like this:
```
#pipeline=[ CONTINUOUS_COPY_NUMBER | FILE ]
#thresholds=-0.7,-0.3,0.3,0.7
#profile_name=Putative copy-number alterations from GISTIC
#profile_description=Putative copy-number calls:  Values: -2=homozygous deletion; -1=hemizygous deletion; 0=neutral/no change; 1=gain; 2=high level amplification```
All key-value pairs **above** are **required**.
```
All key-value pairs **above** are **required**.

The thresholds is a CSV list of numbers in order:
1. `ampl`
2. `gain`
3. `htzd`
4. `hmzd`

## Adding Discrete Copy Number Data

To add **Discrete Copy Number Data** you need to add the key `DISCRETE_COPY_NUMBER` with the relative path to the mutation config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
DISCRETE_COPY_NUMBER	discrete.txt
```
The file `discrete.txt` could look like:

```
#pipeline=CONTINUOUS_COPY_NUMBER
#thresholds=-0.7,-0.3,0.3,0.7
#profile_name=Putative copy-number alterations from GISTIC
#profile_description=Putative copy-number calls:  Values: -2=homozygous deletion; -1=hemizygous deletion; 0=neutral/no change; 1=gain; 2=high level amplification
```
