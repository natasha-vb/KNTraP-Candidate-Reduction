# Main sections based on KNTraP code by Anais Moller

import pandas as pd
import numpy as np
import glob
import argparse
import os
from pathlib import Path
from astropy.table import Table
from astropy.io import fits

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
            "--path_field",
            type=str,
            default="../../workspace/257A_tmpl",
            help="Path to field"
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
    
    

    sci_list = glob.glob("../../workspace/257A_tmpl/1/*.diff.fits")
    diff_list = glob.glob("../../workspace/257A_tmpl/1/*.diff.im.fits")
    tmpl_list = glob.glob("../../workspace/257A_tmpl/1/*.diff.tmpl.fits")