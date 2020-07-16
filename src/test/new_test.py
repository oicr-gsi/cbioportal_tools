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
        self.outDir = os.path.join('/tmp', 'CAP_expression_test')
        test_study = study(os.path.join(self.dataDir, 'CAP_expression', 'study.txt'))
        test_study.write_all(self.outDir)

    def test_file_output(self):
        checksums = {
            'data_clinical_samples.txt': 'b6ab6437e9abbc86bf65f49a4136fe93',
            'meta_clinical_samples.txt': '42609db9577d6192113be9ffeba92292',
            'meta_study.txt': '5ca90314306ad1f1aae94bc345bd0a23'
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
