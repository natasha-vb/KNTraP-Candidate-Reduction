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
            "--ccd",
            type=int,
            help="Selected CCD"
    )
    parser.add_argument(
            "--path_out",
            type=str,
            default="./cats",
            help="Path to outputs"
    )
    parser.add_argument(
            "--test",
            action="store_true",
            help="process one set of images only",
    )
    args = parser.parse_args()

    os.makedirs(args.path_out, exist_ok=True)  



    if args.test:
        print('TESTING FOR A SINGLE IMAGE SET')

        if args.ccd:
            ccds = [args.ccd]
        else:
            ccds = range(1,62,1)

        for ccd in ccds:
            # Read in fits files
            sci_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.fits")
            diff_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.im.fits")
            tmpl_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.tmpl.fits")

            # Sort files in order of date
            sci_list.sort()
            diff_list.sort()
            tmpl_list.sort()

            # verbose option
            print(f'SCIENCE IMAGES, CCD {ccd}:')
            for ii, im in enumerate(sci_list):
                print(sci_list[ii])

            print(f'DIFFERENCE IMAGES, CCD {ccd}:')
            for ii, im in enumerate(diff_list):
                print(diff_list[ii])

            print(f'TEMPLATE IMAGES, CCD {ccd}:')
            for ii, im in enumerate(tmpl_list):
                print(tmpl_list[ii])

            ### PUT IN SOMETHING IN CASE OF EMPTY LIST

            if len(sci_list) == 0:
                print(f"CCD {ccd} IS EMPTY")
            else:
                sci_im = [sci_list[0]]  
                diff_im = [diff_list[0]]  
                tmpl_im = [tmpl_list[0]]  

                print('FIRST FILES IN LIST:')
                print(sci_im)
                print(diff_im)
                print(tmpl_im)

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
            catending = f'{ccd}.sci'
            _,_ = run_sextractor.run_sextractor(sci_im, sextractor_loc = sextractor_loc,
                                                    psfex_loc = psfex_loc, savecats_dir = savecats_dir, 
                                                    spreadmodel = spreadmodel, catending=catending,
                                                    fwhm = fwhm, detect_minarea = detect_minarea, 
                                                    detect_thresh = detect_thresh)
            
            # Run SE on difference image
            # catending = f'{ccd}.diff'
            # _,_ = run_sextractor.run_sextractor_subtractionimage(diff_im, sextractor_loc = sextractor_loc, 
            #                                                         psfex_loc = psfex_loc, savecats_dir = savecats_dir,
            #                                                         catending=catending, fwhm = fwhm, 
            #                                                         detect_minarea = detect_minarea, 
            #                                                         detect_thresh = detect_thresh)

            # Run SE on template image
            # _,_ = run_sextractor.run_sextractor(tmpl_im, sextractor_loc, psfex_loc,
            #                                         savecats_dir,spreadmodel, catending=ccd+'.temp',
            #                                         fwhm, detect_minarea, detect_thresh)


    else:
        
        if args.ccd:
            ccds = args.ccd
        else:
            ccds = range(1,62,1)

        for ccd in ccds:
            # Read in fits files
            sci_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.fits")
            diff_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.im.fits")
            tmpl_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.tmpl.fits")

            sci_list.sort()
            diff_list.sort()
            tmpl_list.sort()

            # should be a verbose option:
            print('FIRST FILES IN LIST:')
            print(sci_list[0])
            print(diff_list[0])
            print(tmpl_list[0])
            
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
            catending = f'{ccd}.sci'
            _,_ = run_sextractor.run_sextractor(sci_list, sextractor_loc = sextractor_loc,
                                                    psfex_loc = psfex_loc, savecats_dir = savecats_dir, 
                                                    spreadmodel = spreadmodel, catending=catending,
                                                    fwhm = fwhm, detect_minarea = detect_minarea, 
                                                    detect_thresh = detect_thresh)
            
            # Run SE on difference image
            catending = f'{ccd}.diff'
            _,_ = run_sextractor.run_sextractor_subtractionimage(diff_list, sextractor_loc, psfex_loc,
                                                                savecats_dir, catending=catending,
                                                                fwhm = fwhm, detect_minarea = detect_minarea, 
                                                                detect_thresh = detect_thresh)

            # Run SE on template image
            catending = f'{ccd}.tmpl'
            # _,_ = run_sextractor.run_sextractor(tmpl_list, sextractor_loc, psfex_loc,
            #                                         savecats_dir,spreadmodel, catending=catending,
            #                                         fwhm = fwhm, detect_minarea = detect_minarea,
            #                                         detect_thresh = detect_thresh)
