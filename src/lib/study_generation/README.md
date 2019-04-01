# Study_Generation
This folder contains the 3 central files for study generation. 

## data.py
This is possibly the most important, it is where when a new feature/data_type is added, the code will be structured.
None of the processing will occur in this file, but rather the larger organization of the conversion of the data for cBioPortal.

To contribute: 
- Add an `elif meta_config.type_config == _____ :` 
- Add relevant functions to the respective `type_config_data.py`  in the `../data_type/` folder
- At the end of the `else if` the data generated **must** be placed into the export folder found in `study_config.config_map['output_folder']`
- Ensure that the appropriate information for the _meta_, _config_, and _case_list_ is in the correct variables in `../constants.py`
  - `meta_info_map`
    - Writes the generic data in the meta_`type`.txt file
  - `args2config_map`
    - If you would like to support the specification of the location of the type_config file in the command line arguments
  - `config2name_map`
    - Gives the respective name to the `meta_{}.txt` and `data_{}.txt` files for a given type
  - `case_list_map`
    - gives correct `case_list` id for given data_type
    
## meta.py
Generates the respective `meta` files for given types. This should likely not need to be modified.
Should you be adding multiple `data_{}.txt` files for a given type:

Do the following:
- Add an `elif config_type == _____ :`
- Call the `generate_meta_type`<sup>1</sup> function with: 
  - Relevant `type_config`
  - A `config_map` mapping the `profile_name` and `profile_description` to respective values
  - The `study_config`

Not much else should be changed. The method is lacking in functionality to add optional options.
  
  
<sup>1</sup> Almost like a recursive call if you think about it.

## case.py

Literally nothing needs to be changed if you continue to use the same architecture (If you're not, then why are you reading this?).
To support more `case_lists` simply add to the `case_list_map`.
