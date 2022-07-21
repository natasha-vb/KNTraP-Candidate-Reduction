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
    
    fp = open(params_name, "w")
    fp.write(f_params)
    fp.close()

    fp.open(conv_name, "w")
    fp.write(f_conv)
    fp.close

    command = sextractor_loc+' -d > '+ config_name
    subprocess.call(command,shell=True)

    command = psfex_loc+' -d > '+ psfconfig_name
    subprocess.call(command,shell=True)

    return None

def remove_temp_files(fs):
    for f in fs:
        os.remove(f)
    return None


def get_psf(fitsfiles, outdir='./', savepsffits=False,
            sextractor_loc = sextractor_loc,
            psfex_loc = psfex_loc):

    create_temp_files(f_conv,f_params,conv_name,params_name,
                      config_name,psfconfig_name,
                      sextractor_loc=sextractor_loc,
                      psfex_loc=psfex_loc)
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    PSFs = []
    if savepsffits:
        PSFfits = []

    for f in fitsfiles:
        cat_out_name_temp = f.replace('.fits', '.psfcat')

        # Run SE on image
        try:
            command = (f'{sextractor_loc} -c {config_name} '
                       f'-MAG_ZEROPOINT 25.0 '
                       f'-CATALOG_TYPE FITS_LDAC '
                       f'-FILTER_NAME {conv_name} '
                       f'-PARAMETERS_NAME {params_name} '
                       f'-CATALOG_NAME {cat_out_name_temp} '
                       f'{f}')
            rval = subprocess.check_call(command,shell=True)
        except subprocess.CalledProcessError as err:
            print('\nCould not run SExtractor with exit error %s\n'%err)
            print('Command used:\n%s\n'%command)
        
        # Run PSFEx on image 
        try:
            if savepsffits:
                command = (f"{psfex_loc} "
                           f"-PSF_DIR {outdir} "
                           f"-c {psfconfig_name} "
                           f"-CHECKIMAGE_TYPE PROTOTYPES "
                           f"-CHECKIMAGE_NAME  proto.fits "
                           f"-PSF_SUFFIX .psf "
                           f"{cat_out_name_temp}")
            else:
                command = (f"{psfex_loc} "
                           f"-PSF_DIR {outdir} "
                           f"-c {psfconfig_name} "
                           f"-CHECKIMAGE_TYPE NONE "
                           f"-CHECKIMAGE_NAME  NONE "
                           f"-PSF_SUFFIX .psf "
                           f"{cat_out_name_temp}")
            subprocess.check_call(command, shell=True)        
        except subprocess.CalledProcessError as err:
            print('Could not run psfex with exit error %s'%err)
        
        remove_temp_files([cat_out_name_temp])

        f_filestub = Path(ntpath.basename(f)).stem

        if savepsffits:
            proto_file = './proto_'+f_filestub+'.fits'
            d_psf = fits.getdata(proto_file)[0:25,0:25]
            PSFfits.append(d_psf)

            f_psffits = outdir+'/'+f_filestub+'_psf.fits'
            fits.writeto(f_psffits, d_psf, overwrite=True)

            os.remove(proto_file)
        
        f_psfbinary = outdir+'/'+f_filestub+'.psf'
        PSFs.append(f_psfbinary)

    remove_temp_files([params_name,conv_name,config_name,psfconfig_name,'psfex.xml'])

    if savepsffits:
        return PSFs, PSFfits
    else:
        return PSFs