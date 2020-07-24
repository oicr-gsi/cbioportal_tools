#! /usr/bin/env python3

import hashlib, logging, os, tempfile, unittest

from generate.study import study

class TestStudy(unittest.TestCase):

    """Tests for Janus study generation"""

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, os.pardir, os.pardir, 'study_input', 'examples_new')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_study_test_')
        self.config_path = os.path.join(self.dataDir, 'CAP_expression', 'study.txt')
        self.base_checksums = {
            'data_cancer_type.txt': 'c23f3a55d260022616a5a95b837c49d0',
            'data_clinical_patients.txt': '852777b8f1bc60b134c9dc999ac87a24',
            'data_clinical_samples.txt': '199053f38a24c52072418a42dba3fdf4',
            'meta_cancer_type.txt': '19d950648288bb7428e8aaf5ee2939a0',
            'meta_clinical_patients.txt': '0de6a7ae349e16b26b68ac5a4eb62a0c',
            'meta_clinical_samples.txt': '42609db9577d6192113be9ffeba92292',
            'meta_study.txt': '5ca90314306ad1f1aae94bc345bd0a23',
            'case_lists/cases_merp.txt': '43685fab767e5961a11e68a45d68c5ec'
        }

    def test_dry_run(self):
        out_dir = os.path.join(self.tmp.name, 'dry_run')
        os.mkdir(out_dir)
        test_study = study(self.config_path, log_level=logging.DEBUG)
        test_study.write_all(out_dir, dry_run=True)
        self.verify_checksums(self.base_checksums, out_dir)

    def test_CAP_expression(self):
        out_dir = os.path.join(self.tmp.name, 'CAP_expression')
        os.mkdir(out_dir)
        test_study = study(self.config_path, log_level=logging.DEBUG)
        test_study.write_all(out_dir, dry_run=False)
        more_checksums = {
            'data_expression_continous.txt', 'e2b50dc44307e0b9bee27d253b02c6d9',
            'data_expression_zscores.txt', '0a04f5f68265ca9a1aded16dd013738c',
            'meta_expression_continous.txt', '5db83d4ca1925117abc8837b2eebeb46',
            'meta_expression_zscores.txt', '4c807196b4d1e1e47710bd96343b3ccc',
        }
        checksums = self.base_checksums.copy()
        checksums.update(more_checksums)
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


if __name__ == '__main__':
    unittest.main()
