# MRNA EXPRESSION ZSCORES Config
This is the specification for the `MRNA_EXPRESSION_ZSCORES` study config files.

This file follows the [standard format](STUDY_CONFIG.md).

### Configuring your data

You need to generate the expression z-scores data from the [MRNA_EXPRESSION.txt](MRNA_EXPRESSION.md) pipeline to use the `SEG` pipeline. The definition for the `FILE` pipeline still needs to be figured out.

### Configuring your header

The minimal header will look like this:
```
#pipeline=[ MRNA_EXPRESSION | FILE]
#profile_name=mRNA Expression zscores data
#profile_description=Expression zscores information (XX Samples)
```
All key-value pairs **above** are **required**.

## Adding Expression Z-Scores Data

To add **Expression Z-Scores Data** you need to add the key `MRNA_EXPRESSION_ZSCORES` with the relative path to the expression config file to the [STUDY_CONFIG.txt](STUDY_CONFIG.md). 

Like this:

```
MRNA_EXPRESSION_ZSCORES	expression_zscores.txt
```
The file `expression_zscores.txt` would look like:

```
#pipeline=MRNA_EXPRESSION
#profile_name=mRNA Expression zscores data
#profile_description=Expression zscores information (05 Samples)
```
- All `data_` type files can be directly imported into the study folder by:
  - Adding `#pipeline=FILE` to the header
  - Having the `dataframe` set as:
  ```
  FILE_NAME
  <LOCATION/OF/FILE.txt>
  ```
  Janus will rename it correctly.