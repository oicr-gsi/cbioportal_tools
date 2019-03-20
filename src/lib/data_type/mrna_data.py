__author__ = "Kunal Chandan"
__license__ = "MIT"
__email__ = "kchandan@uwaterloo.ca"
__status__ = "Pre-Production"

import os
import subprocess

from lib.support import Config, helper

def cufflinks_prep(exports_config: Config.Config, study_config: Config.Config, verb):
    print('lel')