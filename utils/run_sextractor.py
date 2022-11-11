# Based on run_sourceextractor.py code by Jielai Zhang

import ntpath
import os
import random
import shutil
import subprocess

from utils.misc import get_psf

def remove_temp_files(fs):
    for f in fs:
        os.remove(f)
    return None

def remove_temp_dirs(dirs):
    for d in dirs:
        shutil.rmtree(d, ignore_errors=True)
    return None

def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return None

def run_sextractor(fitsfiles, sextractor_loc='sex', psfex_loc='psfex',
                    savecats_dir=None , spreadmodel=True, catending=None,
                    fwhm=1.2, detect_minarea=5, detect_thresh=1.5, ccd=1, 
                    field='257A', diff_im=False, verbose=False):
    
    rand_tmpname = random.randint(10**11,(10**12)-1)

    nnw_path = f"./utils/{rand_tmpname}/default.nnw"
    conv_path = f"./utils/{rand_tmpname}/default.conv" 
    params_path = f"./utils/{rand_tmpname}/default.param"
    config_path = f"./utils/{rand_tmpname}/default.sex"

    make_directory(nnw_path)
    make_directory(conv_path)
    make_directory(params_path)
    make_directory(config_path)

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
            print(f'INTENDED OUTPUT: {catalog_name}\n')

        # Run SE then PSFEx on science/ template image
        if spreadmodel:
            try:
                if verbose:
                    print('----- Currently measuring PSF using Source Extractor and PSFEx\n')
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
            # Grab matching PSF file from science image
            f_psf = catalog_name.replace(f'.diff_{ccd}.diff.cat', '.diff.im.psf')
            if verbose:
                print('PSF FILE NAME: %s\n' % f_psf)
            spreadmodel = True

        # Run SE to get final catalogs
        if PSF_success[ii] == True:
            if spreadmodel:
                command =   f'{sextractor_loc} -c {config_path} '\
                            f'-CATALOG_NAME {catalog_name} '\
                            f'-CATALOG_TYPE ASCII_HEAD '\
                            f'-PARAMETERS_NAME {params_path} -FILTER_NAME {conv_path} '\
                            f'-STARNNW_NAME {nnw_path} -PIXEL_SCALE 0  -MAG_ZEROPOINT 29.2 '\
                            f'-PSF_NAME {f_psf} -PSF_NMAX 1 -PATTERN_TYPE GAUSS-LAGUERRE '\
                            f'-VERBOSE_TYPE {VERBOSE_TYPE} '\
                            f'-SEEING_FWHM {fwhm} -DETECT_MINAREA {detect_minarea} -DETECT_THRESH {detect_thresh} '\
                            f'{f}'
            else:
                command =  f'{sextractor_loc} -c {config_path} '\
                            f'-CATALOG_NAME {catalog_name} '\
                            f'-CATALOG_TYPE ASCII_HEAD '\
                            f'-PARAMETERS_NAME {params_path} -FILTER_NAME {conv_path} '\
                            f'-STARNNW_NAME {nnw_path} -PIXEL_SCALE 0  -MAG_ZEROPOINT 29.2 '\
                            f'-VERBOSE_TYPE {VERBOSE_TYPE} '\
                            f'-SEEING_FWHM {fwhm} -DETECT_MINAREA {detect_minarea} -DETECT_THRESH {detect_thresh} '\
                            f'-CHECKIMAGE_TYPE SEGMENTATION,APERTURES -CHECKIMAGE_NAME seg.fits,aper.fits '\
                            f'-PHOT_APERTURES 8 '\
                            f'{f}'
            if verbose:
                print('----- Currently running source extractor to output required catalog...\n')
                print('----- Executing command: %s\n' % command)
            try:
                rval = subprocess.run(command.split(), check=True)
                catfiles.append(catalog_name)
                catted_fitsfiles.append(f)

                if verbose:
                    print(f'Success! Catalog saved: {catalog_name}\n')
            except subprocess.CalledProcessError as err:
                print('\nCould not run SExtractor with exit error %s\n'%err)
                print('Command used:\n%s\n'%command)
        
        if diff_im:
            spreadmodel=False

    remove_temp_dirs([params_path,conv_path,config_path])

    return catfiles, catted_fitsfiles