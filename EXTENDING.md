# Contributing
To contribute or support another data-type or pipeline, I recommend following these steps as it will ensure the process goes **smoothly**. It will also ensure the **documentation** is also **up to date** with the changes you've made.

The 2 large features that can be implemented are:
* Another data-type e.g., `TIMELINE`, `FUSION`, `MUTSIG`, etc.
* Another **pipeline** for an existing data-type e.g. `CNV-varscan`, `BamMerge`, `starfusion`, etc.

## Supporting a new Data-type

1. Add an `elif meta_config.type_config == 'NEW_TYPE' :` to [`data.py`](src/lib/study_generation/data.py) in the `generate_data_type` function.
   * Please ensure you use the `helper.working_on(verb, message='')` function to help with debugging later.
   * Processing of the actual data should not occur inside this script, but rather in function calls in the next step

2. Add a `<new_type>_data.py`to [`src/lib/data_type/`](src/lib/data_type/)
   * Write functions in `<new_type>_data.py`
   * Call from [`data.py`](src/lib/study_generation/data.py)
   * Try to process multiple files in parallel with `helper.parallel_call()` or `multiprocessing.Pool()`
   * By the end of the `else if` **you must** place the data **you** generate into the export folder found in `study_config.config_map['output_folder']`

3. Support `'FILE'` pipeline:
   * Validation of format in [`data.py`](src/lib/study_generation/data.py) function `assert_format` which should call `<new_type>_data.verify_final_file()`
   * Retrieval of `SAMPLE_ID`s from the file in [`data.py`](src/lib/study_generation/data.py) function `get_sample_ids` which should call `<new_type>_data.get_sample_ids()`

4. Add a `<NEW_TYPE>_CONFIG.md` to [`study_input/Specification/`](study_input/Specification/)

5. Update default constants in [`constants.py`](src/lib/constants/constants.py)
   * `meta_info_map` -> Default `meta_<new_type>.txt`'s values corresponding in order to:
      1. `genetic_alteration_type`
      2. `datatype`
      3. `stable_id`
      4. `show_profile_in_analysis_tab`
      
      (From `general_zip`) or
      
      1. `genetic_alteration_type`
      2. `datatype`
      3. `reference_genome_id`
      
      (From `ref_gene_id_zip`)
      
      Other fields such as optional fields will automatically be written should they be in `optional_fields`.
   * `case_list_map` -> A map that will generate a `cases_(map['NEW_TYPE']).txt` file for a type
      * Please ensure you support retrieval of `SAMPLE_ID`s for the `FILE` pipeline as well
   * `supported_pipe` -> A list of supported pipelines for a given type. By default `'FILE'` pipeline is supported
      * At the very minimum, add the key corresponding to the `'NEW_TYPE'` and an empty list
   
   * `clinical_type` -> **IF** the data is of clinical type, add it to this list.

6. Update help in [`src/lib/support/human_interface.py`](src/lib/support/human_interface.py)
   * Stub should already exist, simply alter the help.



## Supporting a new Pipeline for a Data-type

1. Add an `elif meta_config.config_map['pipeline'] == 'NEW_PIPELINE':` to [`data.py`](data.py)
   * Please ensure you use the `helper.working_on(verb, message='')` function to help with debugging later.
   * Processing of the actual data should not occur inside this script, but rather in function calls in the next step

2. Add relevant functions to the respective `<type>_data.py`  in the [`data_type/`](src/lib/data_type/) folder
   * Write functions in `<new_type>_data.py`
   * Call from [`data.py`](src/lib/study_generation/data.py)
   * Try to process multiple files in parallel with `helper.parallel_call()` or `multiprocessing.Pool()`
   
3. By the end of the `else if` **you must** place the data **you** generate into the export folder found in `study_config.config_map['output_folder']`

4. Add pipeline to [`constants.py`](src/lib/constants/constants.py)
   * `supported_pipe` -> A list of supported pipelines for a given type. By default `'FILE'` pipeline is supported

5. Update [`<TYPE>_CONFIG.md`](study_input/Specification/)
   * Ensure that the README is up-to-date with what is supported