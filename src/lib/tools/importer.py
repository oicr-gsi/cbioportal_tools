__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__version__ = "1.0"
__status__ = "Production"

import os
import argparse
import uuid

from ..support.helper import stars, working_on, call_shell, get_shell, restart_tomcat


def define_parser() -> argparse.ArgumentParser:
    # Define program arguments
    parser = argparse.ArgumentParser(description="Importer script for cBioPortal. Import data_panel, study or both.")
 
    parser.add_argument("-f", "--folder",
                        help="The location of the study folder.",
                        metavar='FOLDER')
    parser.add_argument("-g", "--gene-panel",
                        help="A formatted gene-panel you would like to upload.",
                        metavar='PANEL')
    parser.add_argument("-u", "--url",
                        help="The location of the cBioPortal instance (address).",
                        metavar='URL',
                        required=True)
    parser.add_argument("-k", "--key",
                        help="The location of the cBioPortal Key.",
                        metavar='KEY',
                        default='')
    parser.add_argument("-l", "--user",
                        help="The linux distribution.",
                        metavar='USER',
                        default='Ubuntu - TESTING TESTING TESTING')
    parser.add_argument("-s", "--study_import",
                        help="Use import_study.sh to import by default (import_study) or use metaImport.py to import (metaImport)",
                        metavar='STUDY_IMPORT',
                        default='import_study')
    return parser


def export_study_to_cbioportal(key: str, study_folder: str, cbioportal_url, user, study_import, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    # Copying folder to cBioPortal
    working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))
    
    #Call to access cbioportal
    unique_id = (uuid.uuid1()).int
    new_dir = "~/gsi/{}.{}".format(base_folder, unique_id)
    call_shell("ssh {} {}@{} ' mkdir {}'".format(key, user, cbioportal_url, new_dir), verb)

    # Copy over
    # Check if the files to be imported are files and not directories
    import_files = os.listdir(study_folder)
    for i in range(len(import_files)):
        if os.path.isfile("{}/{}".format(study_folder, import_files[i])):
            print(import_files[i])
            call_shell('scp -r {} {}/{} {}@{}:{}'.format(key, study_folder, import_files[i], user, cbioportal_url, new_dir),
               verb)
        elif os.path.basename(import_files[i]) == "case_lists":
            print(import_files[i])
            call_shell('scp -r {} {}/{} {}@{}:{}'.format(key, study_folder, import_files[i], user, cbioportal_url, new_dir),
               verb)

    working_on(verb)

    # Import study to cBioPortal
    working_on(verb, message='Importing study to cBioPortal...')

    # Old code
    #result = get_shell("ssh {} ubuntu@{} 'cd /home/ubuntu/cbioportal/core/src/main/scripts/importer; "
    #                   "sudo ./metaImport.py -s ~/oicr_studies/{} "
    #                   "-u http://{} -o'; "
    #                   "echo 'CBIOPORTAL_EXIT_CODE:' $?".format(key, cbioportal_url,
    #                                                            base_folder,
    #                                                            cbioportal_url), verb)
    
    # Temporary variables set for testing
    valid = 3
    result = "Testing"

    # Run import_study.sh script if the server uses a docker container
    if study_import == "import_study":
        get_shell("ssh {} -t {}@{} ' /home/ubuntu/import_study.sh {}'".format(key, user, cbioportal_url, new_dir), verb)
    # Run metaImport.py if cbioportal is installed directly on the system
    # No portal checks and override warnings when running metaImport
    elif study_import == "metaImport":
        get_shell("ssh {} -t {}@{} ' /home/ubuntu/metaImport.py -s {} -n -o'".format(key, user, cbioportal_url, new_dir), verb)

    ##### TEST #####
    elif study_import == "test":
        get_shell("ssh {} -t {}@{} ' /home/ubuntu/janus_dev/test_direct.mutation.sh {}'".format(key, user, cbioportal_url, new_dir), verb)

    elif study_import == "CNA":
        get_shell("ssh {} -t {}@{} ' /home/ubuntu/janus_dev/test_direct.CNA.sh {}'".format(key, user, cbioportal_url, new_dir), verb)
    ##### TEST #####
    
    
    # Old code
    #get_shell("ssh {} {}@{} ' ~/import_study.sh {}/'".format(key, user, cbioportal_url, new_dir),verb)
    #result = get_shell ("ssh {} -t {}@{} \ ' ~/import_study.sh ~/gsi/{}/'".format(key, user, cbioportal_url, new_dir), verb)
    #result = get_shell("ssh {} -t {}@{}\ ' /~/import_study.sh /~/gsi/{}'".format(key, user, cbioportal_url, new_dir), verb)
    #                   "echo 'CBIOPORTAL_EXIT_CODE:' $?".format(key, cbioportal_url,
    #                                                            base_folder,
    #                                                            cbioportal_url), verb)

    #print(result)
    #valid = int(list(filter(None, [a if a.startswith('CBIOPORTAL_EXIT_CODE: ') else '' for a in result.split('\n')]))[0].strip('CBIOPORTAL_EXIT_CODE: '))
    #print(valid)

    f = open(os.path.abspath(os.path.join(study_folder, 'import_log.txt')), 'w')
    f.write(result)
    f.flush()
    f.close()

    print('cBioPortal exit code: {}'.format(valid))
    if   valid == 1:
        stars()
        stars()
        print('Validation of study failed. There could be something wrong with the data, please analyse cBioPortal\'s '
              'message above. ')
        stars()
        stars()
        exit(1)
    elif valid == 3:
        stars()
        print('Validation of study succeeded with warnings. Don\'t worry about it, unless you think it\'s important.')
        stars()
    elif valid == 0:
        stars()
        print('This validated with 0 warnings, Congrats!!!')
        stars()
    else:
        stars()
        print('I think something broke really bad, raise an issue about what happened...')
        stars()
        stars()
        exit(1)

    working_on(verb)


def import_portal(key: str, cbioportal_url: str, gene_panel, verb):
    if not key == '':
        key = '-i ' + key

    gene_panel = os.path.abspath(gene_panel)

    stars()
    get_shell("scp {} {} ubuntu@{}:/home/debian/gene_panels/{}".format(key, gene_panel, cbioportal_url, os.path.basename(gene_panel)), verb)

    out = get_shell("ssh {} ubuntu@{} '"
                    "source /etc/profile; "
                    "cd ~/cbioportal/core/src/main/scripts; "
                    "./importGenePanel.pl --data ~/gene_panels/{}'".format(key, cbioportal_url, os.path.basename(gene_panel)), verb)
    print('importing cancer type')
    stars()
    if 'exit status 70.' in out:
        print('There is a missing Identifier/Keyword in the gene_panel file. Or it has been mistyped')
        print(out)
        stars()
        exit(1)

    working_on(verb)


def main(args):
    if not args.gene_panel or args.folder:
        print('ERROR:: Arguments -g/--gene-panel and/or -f/--folder are required.')
    if args.folder:
        export_study_to_cbioportal(args.key, args.folder, args.url, args.user, args.study_import, True)
    #TESTING COPYING TO CBIOPORTAL RIGHT NOW -- COMMENTED OUT IMPORTING TO PORTAL
    #UNCOMMENT TO TEST IMPORTING TO PORTAL
    #if args.gene_panel:
    #    import_portal(args.key, args.url, args.gene_panel, True)get_shell("ssh {} -t {}@{} ' /home/ubuntu/import_study.sh {}'".format(key, user, cbioportal_url, new_dir), verb)
    #get_shell("ssh {} -t {}@{} ' /home/ubuntu/import_study.sh {}'".format(key, user, cbioportal_url, new_dir), verb)
    restart_tomcat(args.url, args.key, True)
