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

from misc import get_psf

def run_sextractor(fitsfiles,spreadmodel = True, catending = None,
                    sextractor_loc, psfex_loc, savecats_dir,
                    fwhm = 1.2, detect_minarea = 5, detect_thresh = 1.5)
    
    nnw_path = "./default.nnw"
    conv_path = "./default.conv" 
    params_path = "./default.param"
    config_path = "./default.sex"

    catfiles = []
    psffiles = []
    catted_fitsfiles = []
    PSF_success = [False]*len(fitsfiles)

    for ii, f in enumerate(fitsfiles):
        fname = ntpath.basename(f)
        if catending:
            catalogue_name = savecats_dir + os.path.sep + fname.replace('.fits','_'+catending+'.cat')
        else:
            catalogue_name = savecats_dir + os.path.sep + fname.replace('.fits','.cat')
    
        if spreadmodel:
          try:
                [f_psf] = get_psf(   ####################      )

                PSF_success[ii] = True

            except:
                print(f'\nSKIPPED: PSF measurement unsuccessful for {f}')
                continue
     else:
            PSF_success[ii] = True
    
     if PSF_success[ii] == True:
        if spreadmodel:
            command =   f'{sextractor_loc} -c {config_path} '\
                        f'-CATALOGUE_NAME {catalogue_name} '\
                        f'-CATALOGUE_TYPE ASCII_HEAD '\
                        f'-PARAMETERS_NAME {params_path} -FILTER_NAME {conv_path} '\
                        f'-STARNNW_NAME {nnw_path} -PIXEL_SCALE 0  -MAG_ZEROPOINT 25.0 '\
                        f'PSF_NAME {f_psf} -PSF_NMAX 1 -PATTERN_TYPE GAUSS-LAGUERRE '\
                        f'-SEEING_FWHM {fwhm} -DETECT_MINAREA {detect_minarea} -DETECT_THRESH {detect_thresh} '\
                        f'{f}'
        else:
             command =  f'{sextractor_loc} -c {config_path} '\
                        f'-CATALOGUE_NAME {catalogue_name} '\
                        f'-CATALOGUE_TYPE ASCII_HEAD '\
                        f'-PARAMETERS_NAME {params_path} -FILTER_NAME {conv_path} '\
                        f'-STARNNW_NAME {nnw_path} -PIXEL_SCALE 0  -MAG_ZEROPOINT 25.0 '\
                        f'PSF_NAME {f_psf} -PSF_NMAX 1 -PATTERN_TYPE GAUSS-LAGUERRE '\
                        f'-SEEING_FWHM {fwhm} -DETECT_MINAREA {detect_minarea} -DETECT_THRESH {detect_thresh} '\
                        f'-CHECKIMAGE_TYPE SEGMENTATION,APERTURES -CHECKIMAGE_NAME seg..fits,aper.fits \'
                        f'-PHOT_APERTURES 8 \'
                        f'{f}'
        
        try:
            rval = subprocess.run(command.split(), check=True)
            catfiles.appead(catalogue_name)
            catted_fitsfiles.append(f)
            if spreadmodel:
                os.remove(f_psf)

        except subprocess.CalledProcessError as err:
            print('\nCould not run SExtractor with exit error %s\n'%err)
            print('Command used:\n%s\n'%command)

    return catfiles, catted_fitsfiles


    