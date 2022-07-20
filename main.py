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

    # read in fits files
    sci_list = glob.glob("../../workspace/257A_tmpl/1/*.diff.fits")
    diff_list = glob.glob("../../workspace/257A_tmpl/1/*.diff.im.fits")
    tmpl_list = glob.glob("../../workspace/257A_tmpl/1/*.diff.tmpl.fits")

    if args.test:
        print("Processing single set:", sci_list[0], diff_list[0], tmpl_list[0])
        sci_im = sci_list[0]
        diff_im = diff_list[0]
        tmpl_im = tmpl_list[0]
    else:
        sci_im = sci_list
        diff_im = diff_list
        tmpl_im = tmpl_list
    
    # SE parameters
    savecats_dir = f"./cats/{args.field}"
    sextractor_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex"
    psfex_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/psfex/3.21.1/bin/psfex"
    spreadmodel = True
    fwhm = 1.2           #default setting
    detect_minarea = 5   #default setting
    detect_thresh = 1.5  #default setting

    #Run SE on science image
    for im in sci_im:
        _,_ = run_sextractor.run_sextractor(im, spreadmodel, catending=None,
                                                sextractor_loc, psfex_loc, savecats_dir,
                                                fwhm, detect_minarea, detect_thresh)
