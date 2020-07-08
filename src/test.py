#! /usr/bin/env python3

import argparse, hashlib, os, tempfile, unittest

from lib.tools import generator

class TestGenerator(unittest.TestCase):

    # run on the GECCO example dataset and validate output
    
    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, '..', 'study_input', 'examples')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_generator_test_')
        self.outDir = os.path.join(self.tmp.name, 'GECCO_test')
        # construct a mock argparse namespace with required parameters
        argsDict = {
            "config": os.path.join(self.dataDir, 'GECCO', 'study.txt'),
            "output_folder": self.outDir,
            "path": os.path.join(self.testDir, '..'),
            "force": True,
            "url": None,
            "key": None,
            "push": False,
            "verbose": False,
        }
        args = argparse.Namespace()
        for key in argsDict.keys():
            setattr(args, key, argsDict[key])
        generator.main(args)

    def test_file_checksums(self):
        expectedChecksums = {
            'data_cancer_type.txt': '0a88403c8412851407f3c1fb6205b527',
            'data_clinical_patients.txt': 'ddb4136eb255888cac8807e493db7249',
            'data_clinical_samples.txt': '23d0fbd36bc48b02a1b6e416f0c712ea',
            'meta_clinical_patients.txt': '7c4b74322a416be75fc34e19031e8adc',
            'meta_clinical_samples.txt': '56c30030759d7f6c1a2b1cae34e84b31',
            'meta_study.txt': '557ba4dd3dc37b89292cf6ab892bb817'
        }
        for fileName in expectedChecksums.keys():
            outPath = os.path.join(self.outDir, fileName)
            self.assertTrue(os.path.exists(outPath), outPath+" exists")
            md5 = hashlib.md5()
            with open(outPath, 'rb') as f:
                md5.update(f.read())
            self.assertEqual(md5.hexdigest(),
                             expectedChecksums[fileName],
                             outPath+" checksums match")

if __name__ == '__main__':
    unittest.main()
