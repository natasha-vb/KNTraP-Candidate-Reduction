import numpy as np
import subprocess
import glob
import argparse


parser = argparse.ArgumentParser(description="Testing detection threshold of Source Extractor")

parser.add_argument(
        "field",
        type=str,
        help="Selected field"
)
parser.add_argument(
        "--ccd",
        type=int,
        help="Selected CCD"
)
parser.add_argument(
        "--path_out",
        type=str,
        default="./thresh_cats",
        help="Path to SE catalogue outputs"
)

parser.add_argument(
        "--test",
        action="store_true",
        help="Process one set of images only"
)
parser.add_argument(
        "--verbose", "--v",
        action="store_true",
        help="Making code more verbose"
)
args = parser.parse_args()

os.makedirs(args.path_out, exist_ok=True)  

# SE parameters
savecats_dir = f"./thresh_cats/{args.field}/{ccd}"
sextractor_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex"
psfex_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/psfex/3.21.1/bin/psfex"
fwhm = 1.2           #default setting
detect_minarea = 5   #default setting
detect_thresh = 1.5  #NAH ITERATE OVER THIS



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

# iterate over detect_thresh from small to large values
# run source extractor with detect_thresh on difference image
# save segmentation map (will count no. objects in jupyter notebook)
# run source extractor on inverted image (inv = 1/diff_image)
# save inverted image segmentation map 