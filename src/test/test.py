#! /usr/bin/env python3

import argparse, hashlib, logging, json, os, random, tempfile, unittest

import pandas as pd

from generate.genetic_alteration import genetic_alteration
from generate.report import report
from generate.sample import sample
from generate.study import study
from support.helper import concat_files, relocate_inputs
from utilities.config import config
from utilities.main import main
from utilities.schema import schema

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

class TestReport(TestBase):
    """Tests for clinical report outout"""

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, os.pardir, os.pardir, 'study_input', 'examples')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_report_test_')

    def test_demo(self):
        """Test with default 'demo' output of the genetic_alteration superclass"""
        random.seed(42)
        out_dir = os.path.join(self.tmp.name, 'test_report_demo')
        #out_dir = '/tmp/janus_report'
        os.mkdir(out_dir)
        with open(os.path.join(self.dataDir, 'json', 'study_config.json')) as configFile:
            config = json.loads(configFile.read())
        test_sample = sample(config['samples'][0]) # use the first sample in the config
        alterations = []
        for alteration_config in config['genetic alterations']:
            alterations.append(genetic_alteration(alteration_config))
        report_name = 'sample_report.json'
        report_path = os.path.join(out_dir, report_name)
        report_config = report(test_sample, alterations).write_report_config(report_path)
        self.assertTrue(os.path.exists(report_path), "JSON report exists")
        checksum = {report_name: '6014b90db5f15bd5def4b5701611d01f'}
        self.verify_checksums(checksum, out_dir)

class TestScript(TestBase):
    """Minimal test of command-line script; other tests run the main() method"""

    def setUp(self):
        super().setUp()
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.scriptName = 'janus.py'
        self.scriptPath = os.path.join(self.testDir, os.pardir, 'bin', self.scriptName)

    def test_compile(self):
        with open(self.scriptPath, 'rb') as inFile:
            compiled = compile(inFile.read(), self.scriptName, 'exec')
        self.assertTrue(True, 'Script compiled without error')

class TestStudy(TestBase):

    """Tests for Janus study generation"""

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, os.pardir, os.pardir, 'study_input', 'examples')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_study_test_')
        self.config_path = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        # clinical patients/samples files currently identical, but this will change
        self.base_checksums = {
            'data_cancer_type.txt': '31d0678d437a5305dcf8e76a9ccc40ff',
            'data_clinical_patients.txt': 'd6fb18fa41b196964b45603fa06daf93',
            'data_clinical_samples.txt': 'd6fb18fa41b196964b45603fa06daf93',
            'meta_cancer_type.txt': '19d950648288bb7428e8aaf5ee2939a0',
            'meta_clinical_patients.txt': '4193bbcfc52c10413c34c2b75d53efc5',
            'meta_clinical_samples.txt': '2b665da238824fc8ee4f44ac1d3d1cc6',
            'meta_study.txt': '58eb6d6b7df072279a9da38be6f82d05',
            'case_lists/cases_3way_complete.txt': 'b5e5d0c300b3365eda75955c1be1f405',
            'case_lists/cases_cnaseq.txt': 'a02611d78ab9ef7d7ac6768a2b9042b7',
            'case_lists/cases_custom.txt': 'f689cf4411b1223a0a907e3e0e48b5d0',
            'case_lists/cases_sequenced.txt': '634dfc2e289fe6877c35b8ab6d31c091'
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
            "which": "generate",
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

    def test_new_config_dry_run(self):
        """Initial test for new config format; will eventually supersede existing tests"""
        out_dir = os.path.join('/tmp', 'janus_study_json_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'json', 'study_config.json')
        self.args.out = out_dir
        main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    ### test legacy copy number alteration pipelines ###

    def test_CAP_CNA_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_CNA_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_CNA', 'study.txt')
        self.args.out = out_dir
        main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_CAP_CNA(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_CNA_dry_run')
        os.mkdir(out_dir)
        self.args.dry_run = False
        self.args.config = os.path.join(self.dataDir, 'CAP_CNA', 'study.txt')
        self.args.out = out_dir
        main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_sequenza_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'sequenza_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'Sequenza', 'study.txt')
        self.args.out = out_dir
        main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_sequenza(self):
        out_dir = os.path.join(self.tmp.name, 'sequenza')
        os.mkdir(out_dir)
        self.args.dry_run = False
        self.args.config = os.path.join(self.dataDir, 'Sequenza', 'study.txt')
        self.args.out = out_dir
        main(self.args)
        checksums = self.base_checksums.copy()
        sequenza_checksums = {
            'data_segments_concat.txt': 'ea71ab46e72eafaaec415f3ed1520c68',
            'meta_segments.txt': '056bc1c506c856f52197389676d9a4d3'
        }
        checksums.update(sequenza_checksums)
        self.verify_checksums(checksums, out_dir)

    ### test legacy expression pipelines ###

    def test_CAP_expression(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_expression')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        main(self.args)
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
        self.args.dry_run = True
        main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_cufflinks(self):
        out_dir = os.path.join(self.tmp.name, 'Cufflinks')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'Cufflinks', 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        main(self.args)
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
        main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    ### test legacy mutation pipelines ###
        
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
            main(self.args)
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
        main(self.args)
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
        self.dataDir = os.path.join(self.testDir, 'data', 'schema')
        self.schema_path = os.path.join(self.dataDir, 'schema1.yaml')
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_schema_test_')

    def test_template(self):
        test_schema = schema(self.schema_path)
        out_dir = os.path.join(self.tmp.name, 'template')
        out_dir = '/tmp/janus'
        os.mkdir(out_dir)
        out_names = ['template%i.txt' % i for i in [1,2,3]]
        template_paths = [os.path.join(out_dir, out_name) for out_name in out_names]
        with open(template_paths[0], 'w') as out_file:
            test_schema.write_template(out_file, describe=False, req_keys=False) # vanilla
        with open(template_paths[1], 'w') as out_file:
            test_schema.write_template(out_file, describe=True, req_keys=False) # more description
        with open(template_paths[2], 'w') as out_file:
            test_schema.write_template(out_file, describe=True, req_keys=True) # even more description
        for template_path in template_paths:
            self.assertTrue(os.path.exists(template_path))
        checksums = {
            out_names[0]: '204860499235bb35448a8b92b62dd07c',
            out_names[1]: 'e0b42022e72ed6e9214b311a45e40841',
            out_names[2]: 'd808e432b81220c103badac36d19cbdb'
        }
        self.verify_checksums(checksums, out_dir)

    def test_validate_syntax(self):
        for good_config in [
                'good_config1.txt', # fully specified config
                'good_config2.txt', # missing optional scalar
                'good_config3.txt', # missing optional dictionary
                'good_config4.txt', # has optional list
        ]:
            config_path = os.path.join(self.dataDir, good_config)
            test_config = config(config_path, self.schema_path, log_level=logging.WARN)
            self.assertTrue(test_config.validate_syntax())
        for bad_config in [
                'bad_config1.txt', # unexpected scalar keys
                'bad_config2.txt', # missing required scalar
                'bad_config3.txt', # extra body column
                'bad_config4.txt', # missing body column
                'bad_config5.txt', # missing required dictionary
                'bad_config6.txt', # unexpected dictionary key
                'bad_config7.txt', # mismatched list contents
        ]:
            config_path = os.path.join(self.dataDir, bad_config)
            test_config = config(config_path, self.schema_path, log_level=logging.ERROR)
            self.assertFalse(test_config.validate_syntax())


if __name__ == '__main__':
    unittest.main()
