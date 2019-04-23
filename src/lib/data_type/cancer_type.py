__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import os

# Data Processing Imports
import pandas as pd

# Data management
from lib.support import Config
from lib.constants import constants


def get_colours(janus_path) -> pd.DataFrame:
    return pd.read_csv(os.path.join(janus_path, constants.colours), header=None, dtype=str)


def gen_cancer_type_data(cancer_type_config: Config.Config, study_config: Config.Config, colours: pd.DataFrame):
    f = open('{}/data_{}.txt'.format(os.path.abspath(study_config.config_map['output_folder']),
                                     cancer_type_config.type_config.lower()), 'w+')
    write_str = []
    for i in range(cancer_type_config.data_frame.shape[0]):
        type_of_cancer = cancer_type_config.data_frame['NAME'][i]
        clinical_trial_keywords = cancer_type_config.data_frame['CLINICAL_TRIAL_KEYWORDS'][i]
        parent_type_of_cancer = cancer_type_config.data_frame['PARENT_TYPE_OF_CANCER'][i]

        name = type_of_cancer.capitalize()

        # Define colour here:
        row = colours[colours[1].str.lower().str.contains(type_of_cancer)]
        try:
            colour = row.iloc[0][2]
        except IndexError: # If none found
            colour = colours.iloc[0][2]

        write_str.append('{}\t{}\t{}\t{}\t{}\r'.format(type_of_cancer,
                                                       name,
                                                       clinical_trial_keywords,
                                                       colour,
                                                       parent_type_of_cancer))
    f.write('\n'.join(write_str))
    f.flush()
    f.close()
