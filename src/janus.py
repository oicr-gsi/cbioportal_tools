__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

# Command Line Imports
import typing

import pandas as pd

# Other Scripts
from lib.support import Config, helper, cbioportal_interface, human_interface
from lib.constants.constants import meta_info_map
from lib.study_generation import data, meta, case

Information = typing.List[Config.Config]


def resolve_priority_queue(information: Information) -> Information:
    score = {}
    # Initialize scores
    for each in information:
        score[each.type_config] = 0

    # Calculate Scores based on directed graph traversal
    for each in information:
        if 'pipeline' in each.config_map.keys():
            type_config = each.config_map['pipeline']
        else:
            continue
        while True:
            if not (type_config in meta_info_map.keys()):
                break
            else:
                score[type_config] += 1
            type_config = [x.config_map['pipeline'] for x in information if x.type_config == type_config]
            if len(type_config) > 1:
                # TODO:: Right now this is not a problem, could this be one day?
                raise ImportError('ERROR:: 2 or more info objects of the same type???')
            else:
                type_config = type_config[0]

    # Sort list based on new scores.
    information.sort(key=lambda config: score [config.type_config], reverse=True)
    return information


def main():
    # TODO:: Ensure absolute paths for helper program files: ie seg2gene.R
    args = human_interface.define_parser().parse_args()
    verb = args.verbose
    path = args.path
    # TODO:: Fail gracefully if something breaks

    if args.config:
        study_config = Config.get_single_config(args.config, 'study', verb)
    else:
        study_config = Config.Config({}, pd.DataFrame(columns=['TYPE', 'FILE_NAME']), 'study')
    human_interface.add_cli_args(study_config, args, verb)

    [information, clinic_data, custom_list] = Config.gather_config_set(study_config, args, verb)

    information = resolve_priority_queue(information)

    [print('Informational Files {}:\n{}\n'.format(a.type_config, a)) for a in information] if verb else print(),
    [print('Clinical List Files {}:\n{}\n'.format(a.type_config, a)) for a in clinic_data] if verb else print(),
    [print('Customized Case Set {}:\n{}\n'.format(a.type_config, a)) for a in custom_list] if verb else print(),

    # Clean Output Folder/Initialize it
    helper.clean_folder(study_config.config_map['output_folder'])

    for each in information:
        meta.generate_meta_type(each.type_config, each.config_map, study_config, verb)
        data.generate_data_type(each, study_config, path, verb)
        case.generate_case_list(each, study_config)

    for each in clinic_data:
        meta.generate_meta_type(each.type_config, each.config_map, study_config, verb)
        data.generate_data_clinical(each, study_config, verb)

    for each in custom_list:
        case.generate_case_list(each, study_config)

    meta.generate_meta_study(study_config, verb)

    # export to cbioportal!
    if args.key or args.push:
        cbioportal_interface.validate_study(args.key, study_config.config_map['output_folder'], verb)
        cbioportal_interface.export_study_to_cbioportal(args.key, study_config.config_map['output_folder'], verb)
        # TODO:: Make the validation step ensure that it doesn't overwrite an existing study

    helper.stars()
    helper.working_on(verb, message='CONGRATULATIONS! Your study should now be imported!')
    helper.stars()
    helper.working_on(verb, message='Output folder: {}'.format(study_config.config_map['output_folder']))
    helper.working_on(verb, message='Study Name: {}'.format(study_config.config_map['name']))
    helper.stars()


if __name__ == '__main__':
    main()
