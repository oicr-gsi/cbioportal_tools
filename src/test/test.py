#! /usr/bin/env python3

import argparse, hashlib, logging, os, tempfile, unittest

import pandas as pd

from generate import generator
from generate.study import study
from support.helper import concat_files, relocate_inputs
from utilities import config

class TestBase(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_test_')
    
    def verify_checksums(self, checksums, out_dir):
        """Checksums is a dictionary: md5sum -> relative path from output directory """
        for relative_path in checksums.keys():
            out_path = os.path.join(out_dir, relative_path)
            self.assertTrue(os.path.exists(out_path), out_path+" exists")
            md5 = hashlib.md5()
            with open(out_path, 'rb') as f:
                md5.update(f.read())
            self.assertEqual(md5.hexdigest(),
                             checksums[relative_path],
                             out_path+" checksums match")

    def tearDown(self):
        self.tmp.cleanup()


class TestStudy(TestBase):

    """Tests for Janus study generation"""

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, os.pardir, os.pardir, 'study_input', 'examples')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_study_test_')
        self.config_path = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.base_checksums = {
            'data_cancer_type.txt': '2756288ed26ccafbf762c52543bd4fe0',
            'data_clinical_patients.txt': '852777b8f1bc60b134c9dc999ac87a24',
            'data_clinical_samples.txt': '199053f38a24c52072418a42dba3fdf4',
            'meta_cancer_type.txt': '19d950648288bb7428e8aaf5ee2939a0',
            'meta_clinical_patients.txt': '0de6a7ae349e16b26b68ac5a4eb62a0c',
            'meta_clinical_samples.txt': '42609db9577d6192113be9ffeba92292',
            'meta_study.txt': '5ca90314306ad1f1aae94bc345bd0a23',
            'case_lists/cases_merp.txt': '43685fab767e5961a11e68a45d68c5ec'
        }

    def test_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'study_dry_run')
        os.mkdir(out_dir)
        test_study = study(self.config_path, log_level=logging.WARN)
        test_study.write_all(out_dir, dry_run=True)
        self.verify_checksums(self.base_checksums, out_dir)



class TestGenerator(TestStudy):

    def setUp(self):
        super().setUp()
        argsDict = {
            "config": None, # placeholder
            "out": None, # placeholder
            "force": False,
            "log_path": None,
            "debug": True,
            "verbose": False,
            "dry_run": True
        }
        self.args = argparse.Namespace()
        for key in argsDict.keys():
            setattr(self.args, key, argsDict[key])

    def test_CAP_CNA_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_CNA_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_CNA', 'study.txt')
        self.args.out = out_dir
        generator.main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_CAP_CNA(self):
        #out_dir = os.path.join(self.tmp.name, 'CAP_CNA_dry_run')
        # temporary out_dir to retain output
        out_dir = os.path.join('/scratch2/users/ibancarz/cbioportal_tools/unittest', 'CAP_CNA')
        os.mkdir(out_dir)
        self.args.dry_run = False
        self.args.config = os.path.join(self.dataDir, 'CAP_CNA', 'study.txt')
        self.args.out = out_dir
        generator.main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)
            
    def test_CAP_expression(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_expression')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        generator.main(self.args)
        checksums = self.base_checksums.copy()
        CAP_expression_checksums = {
            'data_expression_continous.txt': 'e2b50dc44307e0b9bee27d253b02c6d9',
            'data_expression_zscores.txt': '0a04f5f68265ca9a1aded16dd013738c',
            'meta_expression_continous.txt': '5db83d4ca1925117abc8837b2eebeb46',
            'meta_expression_zscores.txt': '4c807196b4d1e1e47710bd96343b3ccc',
            'case_lists/cases_rna_seq_mrna.txt': '1497b32c3999df39b04333da92be5018'
        }
        checksums.update(CAP_expression_checksums)
        self.verify_checksums(checksums, out_dir)

    def test_CAP_expression_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_expression_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        generator.main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_cufflinks(self):
        out_dir = os.path.join(self.tmp.name, 'Cufflinks')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'Cufflinks', 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        generator.main(self.args)
        checksums = self.base_checksums.copy()
        cufflinks_checksums = {
            'data_expression_continous.txt': '0b5d72e82f10637dd791a35a85f08349',
            'data_expression_zscores.txt': '2944c5b792e697eb37976de9225f21fe',
            'meta_expression_continous.txt': '5db83d4ca1925117abc8837b2eebeb46',
            'meta_expression_zscores.txt': '4c807196b4d1e1e47710bd96343b3ccc',
            'case_lists/cases_rna_seq_mrna.txt': '412bd0b09e0a788dd03d7eb9841d271c'
        }
        self.verify_checksums(cufflinks_checksums, out_dir)

    def test_cufflinks_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'Cufflinks_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'Cufflinks', 'study.txt')
        self.args.out = out_dir
        generator.main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_legacy_mutation_dry_run(self):
        """test the legacy mutation scripts in dry-run mode"""
        names = [
            'CAP_mutation',
            #'GATK_haplotype_caller',  # no config in /.mounts/labs/gsiprojects/gsi/cBioGSI/
            'Mutect',
            'Mutect2',
            'MutectStrelka',
            'Strelka'
        ]
        for name in names:
            out_dir = os.path.join(self.tmp.name, name)
            os.mkdir(out_dir)
            self.args.config = os.path.join(self.dataDir, name, 'study.txt')
            self.args.out = out_dir
            generator.main(self.args)
            self.verify_checksums(self.base_checksums, out_dir)

    def test_CAP_mutation(self):
        checksums = {
            'data_mutations_extended.txt': '708506ece7217253432d1eb4c81c7551',
            'meta_mutations_extended.txt': '75c2227886bfe19383e3cc7050042bf9',
            'supplementary_data/unfiltered_data_mutations_extended.txt': 'd7a1303a865c89f268728f3f48c5a13b'
        }
        self.verify_legacy_mutation('CAP_mutation', checksums)

    def test_mutect(self):
        checksums = {
            'data_mutations_extended_concat.txt': 'bdfbf4e37d0edaa6f3df453f51e52f60',
            'meta_mutations_extended.txt': '75c2227886bfe19383e3cc7050042bf9'
        }
        self.verify_legacy_mutation('Mutect', checksums)

    def test_mutect2(self):
        checksums = {
            'data_mutations_extended_concat.txt': '7d7e79afcb521b2375e97303386ca36b',
            'meta_mutations_extended.txt': '75c2227886bfe19383e3cc7050042bf9'
        }
        self.verify_legacy_mutation('Mutect2', checksums)

    def test_mutect_strelka(self):
        checksums = {
            'data_mutations_extended_concat.txt': '66fabfca43cf45fcde568b83fdc0f3e3',
            'meta_mutations_extended.txt': '75c2227886bfe19383e3cc7050042bf9'
        }
        self.verify_legacy_mutation('MutectStrelka', checksums)

    def test_strelka(self):
        checksums = {
            'data_mutations_extended_concat.txt': 'b57da299006a6708a66053da6f552bfd',
            'meta_mutations_extended.txt': '75c2227886bfe19383e3cc7050042bf9'
        }
        self.verify_legacy_mutation('Strelka', checksums)

    def verify_legacy_mutation(self, name, additional_checksums={}):
        """test the legacy mutation scripts for real"""
        out_dir = os.path.join(self.tmp.name, name)
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, name, 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        generator.main(self.args)
        checksums = self.base_checksums.copy()
        checksums.update(additional_checksums)
        self.verify_checksums(checksums, out_dir)

class TestGeneratorMethods(TestBase):

    """Low-level tests of generator methods"""

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.testDir, 'data')
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_generator_method_test_')

    def test_concatenate_files(self):
        test_name = 'concatenate_files'
        input_dir = os.path.join(self.dataDir, test_name)
        out_dir = os.path.join(self.tmp.name, test_name)
        os.mkdir(out_dir)
        inputs = ['foo.tsv', 'bar.tsv', 'baz.tsv']
        df = pd.DataFrame({'FILE_NAME': inputs})
        exports_config = mock_legacy_config({'input_folder': input_dir}, df)
        study_config = mock_legacy_config({'output_folder': out_dir})
        concat_files(exports_config, study_config, True)
        checksums = {'data_mock_concat.txt': 'd5f4cd22aed26f6e5022571ad5f3d745'}
        self.verify_checksums(checksums, out_dir)

    def test_relocate_inputs(self):
        test_name = 'relocate_inputs'
        input_dir = os.path.join(self.dataDir, test_name)
        out_dir = os.path.join(self.tmp.name, test_name)
        os.mkdir(out_dir)
        inputs = ['blue.txt', 'green.tar.gz', 'yellow.tgz', 'purple.tar', 'red.txt.gz']
        df = pd.DataFrame({'FILE_NAME': inputs})
        mutate_config = mock_legacy_config({'input_folder': input_dir}, df)
        study_config = mock_legacy_config({'output_folder': out_dir})
        updated_mutate_config = relocate_inputs(mutate_config, study_config, True)
        outputs = ['blue.txt', 'green/green.txt', 'yellow/yellow.txt', 'purple/purple.txt', 'red.txt']
        md5sum = 'edc715389af2498a623134608ba0a55b' # all output files should be identical
        checksums = {output: md5sum for output in outputs}
        mock_output = os.path.join(out_dir, 'temp', 'temp_mock')
        self.verify_checksums(checksums, mock_output)
        self.assertEqual(updated_mutate_config.config_map['input_folder'],
                         mock_output,
                         'input folder updated')
        outputs = set(['blue.txt', 'green.tar.gz', 'yellow.tgz', 'purple.tar', 'red.txt'])
        self.assertTrue(outputs == set(updated_mutate_config.data_frame['FILE_NAME'].values),
                        'filenames updated')

class mock_legacy_config:

    """Bare-bones mockup of the legacy Config class"""

    def __init__(self, dictionary, data_frame=None, type_config='mock', datahandler='mock', alterationtype='mock'):
        self.config_map = dictionary
        self.data_frame = data_frame
        self.type_config = type_config
        self.datahandler = datahandler
        self.alterationtype = alterationtype

class TestSchema(TestBase):

    """Test the configuration schema: Validation and template generation"""

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.join(self.testDir, 'data')
        self.schema_path = os.path.join(self.dataDir, 'schema', 'test_schema.yaml')
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_schema_test_')

    def test_template(self):
        schema = config.schema(self.schema_path)
        out_dir = self.tmp.name
        template_path = os.path.join(out_dir, 'template.txt')
        with open(template_path, 'w') as out_file:
            schema.write_template(out_file)
        self.assertTrue(os.path.exists(template_path))
        checksums = {'template.txt': 'f221c0e5f905485c86ca6d142a671d84'}
        self.verify_checksums(checksums, out_dir)

    def test_config(self):
        for good_config in ['config1.txt', 'config2.txt']:
            #print('###', good_config)
            config_path = os.path.join(self.dataDir, 'schema', good_config)
            test_config = config.config(config_path, self.schema_path, log_level=logging.WARNING)
            self.assertTrue(test_config.validate_syntax())
        for bad_config in ['config3.txt', 'config4.txt', 'config5.txt', 'config6.txt']:
            #print('###', bad_config)
            config_path = os.path.join(self.dataDir, 'schema', bad_config)
            test_config = config.config(config_path, self.schema_path, log_level=logging.WARNING)
            self.assertFalse(test_config.validate_syntax())


if __name__ == '__main__':
    unittest.main()
