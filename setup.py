"""
Setup script for Janus
"""

import os
from setuptools import setup, find_packages

package_version = '0.0.2'
package_root = 'src/lib'

with open("README.md", "r") as fh:
    long_description = fh.read()

# TODO setup will need to copy R scripts as "data files", when adding pipelines which need them

setup(
    name='Janus',
    version=package_version,
    scripts=['src/bin/janus.py'],
    packages=find_packages(where=package_root),
    package_dir={'' : package_root},
    install_requires=['numpy', 'pandas', 'PyYAML'],
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
