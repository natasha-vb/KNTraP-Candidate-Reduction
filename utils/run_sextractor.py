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

from utils.misc import get_psf

def run_sextractor(fitsfiles, sextractor_loc='sex', psfex_loc='psfex',
                    savecats_dir=None , spreadmodel=True, catending=None,
                    fwhm=1.2, detect_minarea=5, detect_thresh=1.5, ccd=1,
                    diff_im=False, verbose=False):
    
    nnw_path = "./utils/default.nnw"
    conv_path = "./utils/default.conv" 
    params_path = "./utils/default.param"
    config_path = "./utils/default.sex"

    if verbose:
        VERBOSE_TYPE = 'NORMAL'
    else:
        VERBOSE_TYPE = 'QUIET'

    catfiles = []
    psffiles = []
    catted_fitsfiles = []
    PSF_success = [False]*len(fitsfiles)

    # Loop SE over images, one by one
    for ii, f in enumerate(fitsfiles):
        fname = ntpath.basename(f)
        if catending:
            catalog_name = savecats_dir + os.path.sep + fname.replace('.fits','_'+catending+'.cat')
        else:
            catalog_name = savecats_dir + os.path.sep + fname.replace('.fits','.cat')
        
        if verbose:
            print(f'INPUT: {f}')
            print(f'INTENDED OUTPUT: {catalog_name}')

        # Run SE then PSFEx on science/ template image
        if spreadmodel:
            try:
                if verbose:
                    print('Currently measuring PSF using Source Extractor and PSFEx')
                    print('--------------------------------------------------------')
                [f_psf] = get_psf.get_psf([f], outdir=savecats_dir, savepsffits=False,
                                            sextractor_loc=sextractor_loc,
                                            psfex_loc=psfex_loc, catending=None, verbose=verbose)
                PSF_success[ii] = True
            except:
                print(f'\nSKIPPED: PSF measurement unsuccessful for {f}')
                continue
        else:
            PSF_success[ii] = True
        
        if diff_im:
            # Grab matching PSF filename from science image
            f_psf = catalog_name.replace(f'.im_{ccd}.diff.cat', '.psf')
            spreadmodel = True
    
        # Run SE to get final catalogs
            if PSF_success[ii] == True:
                if spreadmodel:
                    command =   f'{sextractor_loc} -c {config_path} '\
                                f'-CATALOG_NAME {catalog_name} '\
                                f'-CATALOG_TYPE ASCII_HEAD '\
                                f'-PARAMETERS_NAME {params_path} -FILTER_NAME {conv_path} '\
                                f'-STARNNW_NAME {nnw_path} -PIXEL_SCALE 0  -MAG_ZEROPOINT 25.0 '\
                                f'-PSF_NAME {f_psf} -PSF_NMAX 1 -PATTERN_TYPE GAUSS-LAGUERRE '\
                                f'-VERBOSE_TYPE {VERBOSE_TYPE} '\
                                f'-SEEING_FWHM {fwhm} -DETECT_MINAREA {detect_minarea} -DETECT_THRESH {detect_thresh} '\
                                f'{f}'
                else:
                    command =  f'{sextractor_loc} -c {config_path} '\
                                f'-CATALOG_NAME {catalog_name} '\
                                f'-CATALOG_TYPE ASCII_HEAD '\
                                f'-PARAMETERS_NAME {params_path} -FILTER_NAME {conv_path} '\
                                f'-STARNNW_NAME {nnw_path} -PIXEL_SCALE 0  -MAG_ZEROPOINT 25.0 '\
                                f'-VERBOSE_TYPE {VERBOSE_TYPE} '\
                                f'-SEEING_FWHM {fwhm} -DETECT_MINAREA {detect_minarea} -DETECT_THRESH {detect_thresh} '\
                                f'-CHECKIMAGE_TYPE SEGMENTATION,APERTURES -CHECKIMAGE_NAME seg.fits,aper.fits '\
                                f'-PHOT_APERTURES 8 '\
                                f'{f}'
                if verbose:
                    print('Currently running source extractor to output required catalog...')
                    print('Executing command: %s\n' % command)
                try:
                    rval = subprocess.run(command.split(), check=True)
                    catfiles.append(catalog_name)
                    catted_fitsfiles.append(f)
                    # if spreadmodel:
                    #     os.remove(f_psf)
                    if verbose:
                        print(f'Success! Catalog saved: {catalog_name}')
                except subprocess.CalledProcessError as err:
                    print('\nCould not run SExtractor with exit error %s\n'%err)
                    print('Command used:\n%s\n'%command)
            
            if diff_im:
                spreadmodel=False

    return catfiles, catted_fitsfiles