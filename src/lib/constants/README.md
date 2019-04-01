# constants

- Ensure that the appropriate information for the _meta_, _config_, and _case_list_ is in the correct variables in `../constants.py`
  - `meta_info_map`
    - Writes the generic data in the meta_`type`.txt file
  - `args2config_map`
    - If you would like to support the specification of the location of the type_config file in the command line arguments
  - `config2name_map`
    - Gives the respective name to the `meta_{}.txt` and `data_{}.txt` files for a given type
  - `case_list_map`
    - Gives correct `case_list` id for given data_type
  - `case_list_map`
    - To support more `case_lists` simply add to the map, gives `stable_id`
