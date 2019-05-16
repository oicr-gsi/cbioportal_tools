# Data_Type Folder
This folder contains all the folders to each pipeline for each data-type.

## Things to Keep in mind

### Conventions
Have a **data_type**__data.py_ python file that will be referenced for script that makes up a *pipeline* in the _data.py_ script in the `../study_generation/` folder.

The **data_type**__data.py_  scripts in each folder should essentially contain simple singular functions that are referenced from each pipeline script in each folder.

Each `DATA_TYPE` folder contains a set of pipeline scripts that are called based on their name.
These pipeline scripts are to call the functions referenced above.

### Processing
Native python is pretty slow and memory intensive and slow, please use `pandas`

### Style
- Keep changes to data simple, this allows for potential reuse between multiple `pipelines` of the same format.
- **Never** change folders of program execution. i.e. `os.chdir`
- Always use absolute paths to prevent ambiguity
