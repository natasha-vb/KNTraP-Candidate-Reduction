# Code from Jielai Zhang

import docopt, os
import astropy.io.fits as fits
import subprocess
from astropy.io import ascii
import pandas as pd
import numpy as np
import ntpath
from pathlib import Path

# create temporary SE files for psf
conv_name = "./temp_default.conv"
params_name = "./temp_params.txt"
config_name = "./temp_default.sex"
psfconfig_name = "./temp_default.psfex"

f_conv = '''CONV NORM
# 3x3 ``all-ground'' convolution mask with FWHM = 2 pixels.
1 2 1
2 4 2
1 2 1'''

f_params='''X_IMAGE
Y_IMAGE
FLUX_RADIUS
FLUX_APER(1)
FLUXERR_APER(1)
ELONGATION
FLAGS
SNR_WIN
VIGNET(35,35)
'''

sextractor_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex"
psfex_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/psfex/3.21.1/bin/psfex"

def create_temp_files(f_conv, f_params, conv_name, params_name,
                        config_name, psfconfig_name,
                        sextractor_loc = sextractor_loc,
                        psfex_loc = psfex_loc)
    
    
