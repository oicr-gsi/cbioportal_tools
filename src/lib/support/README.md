# Support
This folder probably won't change much.

## Config.py
This script contains the data structure definition for the Config objects that are used to manage the data that is imported in cBioPortal.
It also contains a few functions for retrieval of said objects.

## helper.py
This contains some basic functions as well as a few functions that are used across `data_types`. This might change a little?

## cbioportal and human interfaces
2 Scripts containing folders that essentially just interface with their respective names, only contain functions.

This script will need to be modified as new data-types are added.

## cancer_colours.csv
Because cBioPortal wants colours for cancer types, I use this to generate non-conflicting cancer colours, that are also reproducible.

## [import_study.py](import_study.py) & [remove_study.py](remove_study.py)
Standalone CLI scripts for importing and deporting studies in cBioPortal.
