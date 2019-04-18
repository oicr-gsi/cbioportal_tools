import os

from lib.constants.constants import cbioportal_url
from lib.support import helper


def export_study_to_cbioportal(key: str, study_folder: str, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    helper.call_shell("ssh {} debian@{} ' rm -r ~/oicr_studies/{}; mkdir ~/oicr_studies/{}'".format(key,
                                                                                                    cbioportal_url,
                                                                                                    base_folder,
                                                                                                    base_folder), verb)

    # Copy over
    helper.call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_url),
                      verb)

    helper.working_on(verb)

    # Import study to cBioPortal
    helper.working_on(verb, message='Importing study to cBioPortal...')

    helper.call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                      "sudo ./metaImport.py -s ~/oicr_studies/{} "
                      "-u http://{} -o'".format(key, cbioportal_url,
                                                base_folder,
                                                cbioportal_url), verb)

    helper.call_shell("ssh {} debian@{} 'sudo systemctl stop  tomcat'".format(key, cbioportal_url), verb)
    helper.call_shell("ssh {} debian@{} 'sudo systemctl start tomcat'".format(key, cbioportal_url), verb)

    helper.working_on(verb)


def validate_study(key, study_folder, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    log_file = os.path.join(os.path.abspath(study_folder), 'import_log.txt')
    # Copying folder to cBioPortal
    helper.working_on(verb, message='Validating study ...')

    helper.call_shell("ssh {} debian@{} ' rm -r ~/oicr_studies/{}; mkdir ~/oicr_studies/{}'".format(key,
                                                                                                    cbioportal_url,
                                                                                                    base_folder,
                                                                                                    base_folder), verb)

    # Copy over
    helper.call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_url),
                      verb)

    helper.working_on(verb)

    # Import study to cBioPortal
    helper.working_on(verb, message='Validating study via cBioPortal...')

    valid = helper.call_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                              "sudo ./validateData.py -s ~/oicr_studies/{} "
                              "-u http://{}' | "
                              "tee {}".format(key, cbioportal_url,
                                              base_folder,
                                              cbioportal_url,
                                              log_file), verb)

    if   valid == 1:
        helper.stars()
        helper.stars()
        print('Validation of study failed. There could be something wrong with the data, please analyse cBioPortal\'s '
              'message above. ')
        exit(1)
        helper.stars()
        helper.stars()
    elif valid == 3 or valid == 0:
        helper.stars()
        print('Validation of study succeeded with warnings. Don\'t worry about it, unless you think it\'s important.')
        helper.stars()
    else:
        helper.stars()
        helper.stars()
        print('I think something broke really bad, raise an issue about what happened...')
        exit(1)
    helper.working_on(verb)
