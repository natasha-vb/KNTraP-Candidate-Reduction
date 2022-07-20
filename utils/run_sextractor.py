# Based on run_sourceextractor.py code by Jielai Zhang

import docopt, os
import astropy.io.fits as fits
import subprocess
from astropy.io import ascii
import pandas as pd
import numpy as np
import ntpath, shutil
import time
import string    
import random
import shutil

from misc import get_psf

def run_sextractor(fitsfiles,spreadmodel=True, 
                    sextractor_loc, psfex_loc, savecats_dir,
                    fwhm = 1.2, detect_minarea = 5, detect_thresh = 1.5)
