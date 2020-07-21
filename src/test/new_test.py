#! /usr/bin/env python3

import hashlib, os, tempfile, unittest

from generate.study import study

class TestStudy(unittest.TestCase):

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, os.pardir, os.pardir, 'study_input', 'examples_new')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_study_test_')
        #self.outDir = os.path.join(self.tmp.name, 'CAP_expression_test')
        #os.mkdir(self.outDir)
        ### temporary setup for output directory -- won't be deleted on test exit
        self.outDir = os.path.join('/tmp', 'CAP_expression_test')
        from shutil import rmtree
        if os.path.exists(self.outDir):
            rmtree(self.outDir)
        os.mkdir(self.outDir)
        ###
        test_study = study(os.path.join(self.dataDir, 'CAP_expression', 'study.txt'))
        test_study.write_all(self.outDir)

    def test_file_output(self):
        checksums = {
            'data_cancer_type.txt': 'c23f3a55d260022616a5a95b837c49d0',
            'data_clinical_patients.txt': '852777b8f1bc60b134c9dc999ac87a24',
            'data_clinical_samples.txt': '199053f38a24c52072418a42dba3fdf4',
            'meta_cancer_type.txt': '19d950648288bb7428e8aaf5ee2939a0',
            'meta_clinical_patients.txt': '0de6a7ae349e16b26b68ac5a4eb62a0c',
            'meta_clinical_samples.txt': '42609db9577d6192113be9ffeba92292',
            'meta_study.txt': '5ca90314306ad1f1aae94bc345bd0a23',
            'case_lists/cases_merp.txt': '43685fab767e5961a11e68a45d68c5ec'
        }
        for name in checksums.keys():
            outPath = os.path.join(self.outDir, name)
            self.assertTrue(os.path.exists(outPath), outPath+" exists")
            md5 = hashlib.md5()
            with open(outPath, 'rb') as f:
                md5.update(f.read())
            self.assertEqual(md5.hexdigest(),
                             checksums[name],
                             outPath+" checksums match")

    def tearDown(self):
        self.tmp.cleanup()


if __name__ == '__main__':
    unittest.main()
