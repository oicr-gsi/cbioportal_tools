"""
Setup script for Janus
"""

import os
from setuptools import setup, find_packages

package_version = '0.0.3'
package_root = 'src/lib'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='janus',
    version=package_version,
    scripts=['src/bin/janus.py'],
    packages=find_packages(where=package_root),
    package_dir={'' : package_root},
    package_data={
        'generate': [
            'data/cancer_colours.csv'
        ],
        'generate.analysis_pipelines.COPY_NUMBER_ALTERATION': [
            'data/hmmcopy_chrom_positions.txt',
            'data/ncbi_genes_hg19_canonical.bed',
            'data/targeted_genelist.txt',
            'R_scripts/preProcCNA.r',
            'R_scripts/seg2gene.r'
        ],
        'generate.analysis_pipelines.MRNA_EXPRESSION': [
            'data/targeted_genelist.txt',
            'data/ensemble_conversion.txt'
        ],
        'generate.analysis_pipelines.MUTATION_EXTENDED': [
            'data/vep_keep_columns.txt'
        ]
    },
    install_requires=['numpy', 'pandas', 'scipy', 'PyYAML'],
    python_requires='>=3.7',
    author="Iain Bancarz",
    author_email="ibancarz@oicr.on.ca",
    description="Gateway for cBioPortal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oicr-gsi/cbioportal_tools",
    keywords=['cancer', 'bioinformatics', 'cBioPortal'],
    license='GPL 3.0',
)
