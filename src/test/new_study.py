# Collect names of mutation files and convert them to PATIENT_IDs and SAMPLE_IDs
# Script maps each file to a patient ID.
import os

path = 'fakes/'

os.chdir(path)
files = os.listdir(".")
files.sort()

key_val = []
for each in files:
    if each.endswith('.gz'):
        each = each[:-3]
    if each.endswith('.vcf'):
        each = each[:-4]
    if each.endswith('.maf'):
        each = each[:-4]
    split = each.split("_")
    patient_id = []
    # Gen Patient ID from file name of the form "stringNumber"
    for every in split:
        try:
            patient_id += every + '_'
            int(every)
            break
        except ValueError:  # Catch and do nothing
            continue

    patient_id = ''.join(patient_id[:-1])
    print(patient_id)
    key_val += [patient_id, each]
# print key_val
# key_val is a map for all files to their relevant patient_id.

# Next the data needs to be turned into a dataframe that will be written into the data_samples.txt
import numpy as np

key_val = np.reshape(key_val, (len(key_val)/2, 2))
# key_val is now reshaped to a 2D array where a patient ID corresponds to a sample ID
print(key_val)

import pandas as pd
dataset = pd.DataFrame({'PATIENT_ID': key_val[:, 0], 'SAMPLE_ID': key_val[:, 1]}, index=False)

print(dataset)
os.chdir('../')

new_study_folder = 'lololol/'

if not os.stat(new_study_folder):
    os.mkdir(new_study_folder)
os.chdir(new_study_folder)
dataset.to_csv('data_' + path[:-1] + '.tsv', sep='\t')

