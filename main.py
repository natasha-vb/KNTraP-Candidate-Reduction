# Main sections based on KNTraP code by Anais Moller

import pandas as pd
import numpy as np
import glob
import argparse
import os
from pathlib import Path
from astropy.table import Table
from astropy.io import fits

from utils import run_sextractor

def read_file(fname):
    try:
        df_tmp = Table.read(fname, format="ascii").to_pandas()
        df = pd.read_table(fname, header=None, skiprows=1, delim_whitespace=True)
        df.columns = [
                    "MJD",
                    "dateobs",
                    "photcode",
                    "filt",
                    "flux_c",
                    "dflux_c",
                    "type",
                    "chisqr",
                    "ZPTMAG_c",
                    "m",
                    "dm",
                    "ra",
                    "dec",
                    "cmpfile",
                    "tmpl",
                ]
        df_tmp = df.copy()

        return df_tmp

    except Exception:
        print("File corrupted or empty", fname)
        df_tmp = pd.DataFrame()
        return df_tmp


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Source Extractor to filter transient candidates")

    parser.add_argument(
            "field",
            type=str,
            help="Selected field"
    )
    parser.add_argument(
            "--path_out",
            type=str,
            default="./SE_outputs",
            help="Path to outputs"
    )
    parser.add_argument(
            "--test",
            action="store_true",
            default="process one set of images only",
    )
    args = parser.parse_args()

    os.makedirs(args.path_out, exist_ok=True)  

    # Loop over every CCD

    ccds = range(1,62,1)

    if args.test:
        ccd = 1

        # Read in fits files
        sci_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.fits")
        diff_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.im.fits")
        tmpl_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.tmpl.fits")

        # Sort files in order of date
        sci_list.sort()
        diff_list.sort()
        tmpl_list.sort()

        print('SCIENCE IMAGES:')
        for ii, im in enumerate(sci_list):
            print(sci_list[ii])

        print('DIFFERENCE IMAGES:')
        for ii, im in enumerate(diff_list):
            print(diff_list[ii])

        print('TEMPLATE IMAGES:')
        for ii, im in enumerate(tmpl_list):
            print(tmpl_list[ii])

        print('First files in list:')
        print(sci_list[0])
        print(diff_list[0])
        print(tmpl_list[0])
        
        # SE parameters
        savecats_dir = f"./cats/{args.field}"
        sextractor_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex"
        psfex_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/psfex/3.21.1/bin/psfex"
        spreadmodel = True
        fwhm = 1.2           #default setting
        detect_minarea = 5   #default setting
        detect_thresh = 1.5  #default setting

        print(savecats_dir)

    else:
        # for ccd in ccds:

        ccd = 1
                
        # Read in fits files
        sci_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.fits")
        diff_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.im.fits")
        tmpl_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.tmpl.fits")

        sci_list.sort()
        diff_list.sort()
        tmpl_list.sort()

        print('FIRST FILES IN LIST:')
        print(sci_list[0])
        print(diff_list[0])
        print(tmpl_list[0])
    
        sci_im = sci_list[0]
        diff_im = diff_list[0]
        tmpl_im = tmpl_list[0]
        
        # SE parameters
        savecats_dir = f"./cats/{args.field}/{ccd}"
        sextractor_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex"
        psfex_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/psfex/3.21.1/bin/psfex"
        spreadmodel = True
        fwhm = 1.2           #default setting
        detect_minarea = 5   #default setting
        detect_thresh = 1.5  #default setting

        print('SAVE CATALOG DIRECTORY: ', savecats_dir)

        # Run SE on science image
        _,_ = run_sextractor.run_sextractor(sci_im, sextractor_loc, psfex_loc, 
                                                savecats_dir, spreadmodel, catending=ccd+'.sci',
                                                fwhm = fwhm, detect_minarea = detect_minarea, 
                                                detect_thresh = detect_thresh)
        
        # Run SE on difference image
        # _,_ = run_sextractor.run_sextractor_subtractionimage(sci_im, sextractor_loc, psfex_loc,
        #                                                     savecats_dir, spreadmodel, catending=ccd+'.diff',
        #                                                     fwhm, detect_minarea, detect_thresh)


        # Run SE on template image
        # _,_ = run_sextractor.run_sextractor(tmpl_im, sextractor_loc, psfex_loc,
        #                                         savecats_dir,spreadmodel, catending=ccd+'.temp',
        #                                         fwhm, detect_minarea, detect_thresh)

        
######################## ERROR MESSAGE:
# File "main.py", line 151

#               ^
# SyntaxError: positional argument follows keyword argument