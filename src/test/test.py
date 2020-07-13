#! /usr/bin/env python3

import argparse, hashlib, os, tempfile, unittest

from lib.tools import generator

class TestGeneratorCAPExpression(unittest.TestCase):

    # run on the CAP expression dataset and validate output

    def setUp(self):
        self.testDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = os.path.realpath(
            os.path.join(self.testDir, os.pardir, os.pardir, 'study_input', 'examples')
        )
        self.tmp = tempfile.TemporaryDirectory(prefix='janus_generator_test_')
        self.outDir = os.path.join(self.tmp.name, 'CAP_expression_test')
        # construct a mock argparse namespace with required parameters
        argsDict = {
            "config": os.path.join(self.dataDir, 'CAP_expression', 'study.txt'),
            "output_folder": self.outDir,
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
        mainChecksums = {
            'data_cancer_type.txt': 'd2000eb8d7355ef81a6d9c10bcca73af',
            'data_clinical_patients.txt': '852777b8f1bc60b134c9dc999ac87a24',
            'data_clinical_samples.txt': '199053f38a24c52072418a42dba3fdf4',
            'data_expression_continous.txt': 'e2b50dc44307e0b9bee27d253b02c6d9',
            'data_expression_zscores.txt': '0a04f5f68265ca9a1aded16dd013738c',
            'meta_clinical_patients.txt': '59c55f5e4578f70e40f3b44d01d5baff',
            'meta_clinical_samples.txt': '40543f66af0e05da059b569df6ff199c',
            'meta_expression_continous.txt': '5db83d4ca1925117abc8837b2eebeb46',
            'meta_expression_zscores.txt': '4c807196b4d1e1e47710bd96343b3ccc',
            'meta_study.txt': 'd980b676d68ffacfd74ff32d233bc731'
        }
        caseListChecksums = {
            'cases_merp.txt': '43685fab767e5961a11e68a45d68c5ec',
            'cases_rna_seq_mrna.txt': '1497b32c3999df39b04333da92be5018'
        }
        supplementaryChecksums = {
            'data_expression_percentile.txt': 'e1f603df04a6b6c32b8bceee912420c8',
            'data_expression_percentile_comparison.txt': 'e1f603df04a6b6c32b8bceee912420c8',
            'data_expression_percentile_tcga.txt': '597244ff8dd79c2bea46bb3bbb79278f',
            'data_expression_zscores_comparison.txt': '4cd93477b3bb87f3aadeaebd25b4819f',
            'data_expression_zscores_tcga.txt': 'e7bf737453a5298a849e2b76f6d40f3b'
        }
        # TODO also check the supplementary_data directory
        allChecksums = {}
        for fileName in mainChecksums.keys():
            allChecksums[os.path.join(self.outDir, fileName)] = mainChecksums[fileName]
        for fileName in caseListChecksums.keys():
            allChecksums[os.path.join(self.outDir, 'case_lists', fileName)] = caseListChecksums[fileName]
        for fileName in supplementaryChecksums.keys():
            allChecksums[os.path.join(self.outDir, 'supplementary_data', fileName)] = supplementaryChecksums[fileName]
        for outPath in allChecksums.keys():
            self.assertTrue(os.path.exists(outPath), outPath+" exists")
            md5 = hashlib.md5()
            with open(outPath, 'rb') as f:
                md5.update(f.read())
            self.assertEqual(md5.hexdigest(),
                             allChecksums[outPath],
                             outPath+" checksums match")

class TestGeneratorGECCO(unittest.TestCase):

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
