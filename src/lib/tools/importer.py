__author__ = "Kunal Chandan"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "1.0"

import os
import argparse

from ..support.helper import stars, working_on, call_shell, get_shell


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
    return parser


def export_study_to_cbioportal(key: str, study_folder: str, cbioportal_url, verb):
    if not key == '':
        key = '-i ' + key
    base_folder = os.path.basename(os.path.abspath(study_folder))
    log_file = os.path.join(os.path.abspath(study_folder), 'import_log.txt')
    # Copying folder to cBioPortal
    working_on(verb, message='Copying folder to cBioPortal instance at {} ...'.format(cbioportal_url))

    call_shell("ssh {} debian@{} ' rm -r ~/oicr_studies/{}; mkdir ~/oicr_studies/{}'".format(key,
                                                                                             cbioportal_url,
                                                                                             base_folder,
                                                                                             base_folder), verb)

    # Copy over
    call_shell('scp -r {} {} debian@{}:/home/debian/oicr_studies/'.format(key, study_folder, cbioportal_url),
               verb)

    working_on(verb)

    # Import study to cBioPortal
    working_on(verb, message='Importing study to cBioPortal...')

    result = get_shell("ssh {} debian@{} 'cd /home/debian/cbioportal/core/src/main/scripts/importer; "
                       "sudo ./metaImport.py -s ~/oicr_studies/{} "
                       "-u http://{} -o'; "
                       "echo 'CBIOPORTAL_EXIT_CODE:' $?".format(key, cbioportal_url,
                                        base_folder,
                                        cbioportal_url), verb)
    print(result)
    valid = int(list(filter(None, [a if a.startswith('CBIOPORTAL_EXIT_CODE: ') else '' for a in result.split('\n')]))[0].strip('CBIOPORTAL_EXIT_CODE: '))
    print(valid)

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
    get_shell("scp {} {} debian@{}:/home/debian/gene_panels/{}".format(key, gene_panel, cbioportal_url, os.path.basename(gene_panel)), verb)

    out = get_shell("ssh {} debian@{} '"
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


def restart_tomcat(cbioportal_url, key, verb):
    call_shell("ssh {} debian@{} 'sudo systemctl stop  tomcat'".format(key, cbioportal_url), verb)
    call_shell("ssh {} debian@{} 'sudo systemctl start tomcat'".format(key, cbioportal_url), verb)


def main(args):
    if args.folder:
        export_study_to_cbioportal(args.key, args.folder, args.url, True)
    elif args.gene_panel:
        import_portal(args.key, args.url, args.gene_panel, True)
    restart_tomcat(args.url, args.key, True)
