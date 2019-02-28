__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import os

# Data management
import Config

# Data Processing Imports
import pandas as pd


def get_colours() -> pd.DataFrame:
    return pd.read_csv('cancer_colours.csv', delimiter=',', header=None)


def gen_cancer_type_data(cancer_type_config: Config.Config, study_config: Config.Config, colours: pd.DataFrame):
    f = open('{}/data_{}.txt'.format(os.path.abspath(study_config.config_map['output_folder']),
                                     cancer_type_config.type_config), 'w+')
    write_str = []
    for i in range(cancer_type_config.data_frame.shape[0]):
        type_of_cancer = cancer_type_config.data_frame['name'][i]
        clinical_trial_keywords = cancer_type_config.data_frame['clinical_trial_keywords'][i]
        name = type_of_cancer.capitalize()

        # Define colour here:
        row = colours[colours[1].str.lower().str.contains(type_of_cancer)]
        try:
            colour = row.iloc[0][2]
        except KeyError: # If none found
            colour = colours.iloc[0][2]


        parent_type_of_cancer = 'tissue'
        write_str.append('{}\t{}\t{}\t{}\t{}\r'.format(type_of_cancer,
                                                       name,
                                                       clinical_trial_keywords,
                                                       colour,
                                                       parent_type_of_cancer))
    f.write('\n'.join(write_str))
    f.close()
