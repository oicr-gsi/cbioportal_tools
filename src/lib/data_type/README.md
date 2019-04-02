# Data_Type Folder
This folder will and does contain all the scripts for converting, generating and altering data that will be imported into cBioPortal.

## Things to Keep in mind

### Conventions
Have a **data_type**__data.py_ python file that will be referenced from the _data.py_ script in the `../study_generation/` folder.
The scripts in this folder should essentially run simple singular functions that are referenced from _data.py_.

For the future, consider refactoring this folder to have sub-folders depending on language or more likely `data_type`.

### Processing
I do **not** recommend doing much if any data processing in Python.
Python is pretty slow and memory intensive. I recommend generating `awk`, `sed`, `grep` or any other shell script that does the actual processing.

`awk` is a fairly legible language that I have seen to be many 10s if not 100s of times faster than Python for the same data processing.
You will need to output to a temporary file and move it back to the original file.

### Style
- Keep changes to data simple, this allows for potential reuse between multiple `pipelines` of the same format.
- **Never** change folders of program execution. ie `os.chdir`
