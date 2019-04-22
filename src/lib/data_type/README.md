# Data_Type Folder
This folder will and does contain all the scripts for converting, generating and altering data that will be imported into cBioPortal.

## Things to Keep in mind

### Conventions
Have a **data_type**__data.py_ python file that will be referenced from the _data.py_ script in the `../study_generation/` folder.
The scripts in this folder should essentially run simple singular functions that are referenced from _data.py_.

For the future, consider refactoring this folder to have sub-folders depending on language or more likely `data_type`.

### Processing
Native python is pretty slow and memory intensive and slow, please use `pandas`

### Style
- Keep changes to data simple, this allows for potential reuse between multiple `pipelines` of the same format.
- **Never** change folders of program execution. ie `os.chdir`
