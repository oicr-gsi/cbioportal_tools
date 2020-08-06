#! /usr/bin/env python3

import argparse, hashlib, logging, os, tempfile, unittest

from generate import generator
from generate.study import study

class TestStudy(unittest.TestCase):

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
        self.CAP_expression_checksums = {
            'data_expression_continous.txt': 'e2b50dc44307e0b9bee27d253b02c6d9',
            'data_expression_zscores.txt': '0a04f5f68265ca9a1aded16dd013738c',
            'meta_expression_continous.txt': '5db83d4ca1925117abc8837b2eebeb46',
            'meta_expression_zscores.txt': '4c807196b4d1e1e47710bd96343b3ccc',
            'case_lists/cases_rna_seq_mrna.txt': '1497b32c3999df39b04333da92be5018'
        }

    def test_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'study_dry_run')
        os.mkdir(out_dir)
        test_study = study(self.config_path, log_level=logging.WARN)
        test_study.write_all(out_dir, dry_run=True)
        self.verify_checksums(self.base_checksums, out_dir)

    def OMIT_test_CAP_expression(self):
        # omit this test for now; largely redundant with TestGenerator.test_CAP_expression
        out_dir = os.path.join(self.tmp.name, 'study_CAP_expression')
        os.mkdir(out_dir)
        test_study = study(self.config_path, log_level=logging.WARN)
        test_study.write_all(out_dir, dry_run=False)
        checksums = self.base_checksums.copy()
        checksums.update(self.CAP_expression_checksums)
        self.verify_checksums(checksums, out_dir)

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

    def test_CAP_expression(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_expression')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        generator.main(self.args)
        checksums = self.base_checksums.copy()
        checksums.update(self.CAP_expression_checksums)
        self.verify_checksums(checksums, out_dir)

    def test_CAP_expression_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_expression_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.args.out = out_dir
        generator.main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)

    def OMIT_test_CAP_mutation(self):
        # live test not working yet; seems to assume MAF.py has been run first
        out_dir = os.path.join(self.tmp.name, 'CAP_mutation_dry_run')
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, 'CAP_mutation', 'study.txt')
        out_dir = '/tmp/CAP_mutation' # FIXME
        self.args.out = out_dir
        self.args.dry_run = False
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
        self.verify_legacy_mutation('CAP_mutation')

    def test_mutect(self):
        self.verify_legacy_mutation('Mutect')

    def test_mutect2(self):
        self.verify_legacy_mutation('Mutect2')

    def test_mutect_strelka(self):
        self.verify_legacy_mutation('MutectStrelka')

    def test_strelka(self):
        self.verify_legacy_mutation('Strelka')

    def verify_legacy_mutation(self, name):
        """test the legacy mutation scripts for real"""

        #out_dir = os.path.join(self.tmp.name, name)
        # FIXME temporary hack to retain out_dir
        out_dir = os.path.join('/scratch2/users/ibancarz/cbioportal_tools/unittest/', name)
        os.mkdir(out_dir)
        self.args.config = os.path.join(self.dataDir, name, 'study.txt')
        self.args.out = out_dir
        self.args.dry_run = False
        generator.main(self.args)
        self.verify_checksums(self.base_checksums, out_dir)



if __name__ == '__main__':
    unittest.main()
