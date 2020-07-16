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
        study_meta_file = os.path.join(self.outDir, 'meta_study.txt')
        self.assertTrue(os.path.exists(study_meta_file))

    def tearDown(self):
        self.tmp.cleanup()


if __name__ == '__main__':
    unittest.main()
