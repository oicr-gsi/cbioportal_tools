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

## Contribution

### Constants
- Ensure that the appropriate information for the _meta_, _config_, and _case_list_ is in the correct variables in [`constants.py`](../constants/constants.py)
  - `meta_info_map`
    - Writes the generic data in the `meta_<type>.txt` file
  - `args2config_map`
    - To support the specification of the location of the type_config file in the command line arguments
    - A unique identifier that then requires you to add this to the parser in [`janus.py`](../../janus.py)
      - After adding there, call `python3 janus.py -h` and paste the output to the [`README.md`](../../README.md)
  - `config2name_map`
    - Gives the respective name to the `meta_{}.txt` and `data_{}.txt` files for a given type
    - Can be arbitrary
  - `case_list_map`
    - gives correct `case_list` id for given data_type
    - Honestly I'm a little lost as to how this affects the actual study since case lists still show up regardless of them existing in this map.

### Pipelines

1. Add an `elif meta_config.type_config == _____ :` to [`data.py`](data.py)
2. Add relevant functions to the respective `<type>_data.py`  in the [`../data_type/`](../data_type) folder
3. Assert the correct pipeline using [`helper.assert_pipe()`](../support/helper.py)
4. Call the relevant functions based on `meta_config.config_map['pipeline']`
5. By the end of the `else if` **you must** place the data **you** generate into the export folder found in `study_config.config_map['output_folder']`
