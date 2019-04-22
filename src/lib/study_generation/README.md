# Study_Generation/Contribution
This folder contains the 3 central files for study generation. 

## [`data.py`](data.py)
This is possibly the most important, it is where when a new feature/data_type is added, the code will be structured.
None of the processing will occur in this file, but rather the larger organization of the conversion of the data for cBioPortal.

## [`meta.py`](meta.py)
Generates the respective `meta` files for given types. This should likely not need to be modified.
Not much else should be changed. The method is lacking in functionality to add optional options.

## [`case.py`](case.py)

Literally nothing needs to be changed if you continue to use the same architecture (If you're not, then why are you reading this?).
To support more `case_lists` simply add to the `case_list_map` (in [`constants.py`](../constants/constants.py)).
