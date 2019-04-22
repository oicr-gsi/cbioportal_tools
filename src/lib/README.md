# lib
This folder should contain nothing but this and other folders.
- In here is a general organization of the scripts that do the heavy-lifting of making a viable study.
- [`study_generation`](study_generation/): High level of each type of file and each pipeline it can process.
- [`data_type`](data_type/): Actual processing of each piece of data
- [`constants`](constants/) & [`support`](support/): Other functions and data used by above 2

#### Standalone scripts:
* [`import_study.py`](support/import_study.py) -> import a pre-configured study
* [`remove_study.py`](support/remove_study.py) -> remove a study based on ID
