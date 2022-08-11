# Sections based on KNTraP code by Anais Moller

import pandas as pd
import numpy as np
import glob
import argparse
import os
import re 
from pathlib import Path
from astropy.table import Table
from astropy.io import fits
import astropy.io.ascii as ascii

from utils import run_sextractor

def cat_match(date, ra, dec, filt, field='257A', ccd='1'):
        match_list = glob.glob(f'./cats/{field}/{ccd}/*.{date}.*_{filt}_*.cat')
        df_cattmp = pd.DataFrame()

        for m in match_list:
            cat = ascii.read(m)
            df_cat = pd.DataFrame(cat.as_array())
        
            err = 0.001
            match = df_cat[(df_cat["X_WORLD" < (ra+err)]) & (df_cat["X_WORLD" > (ra-err)])
                            (df_cat["Y_WORLD" < (dec+err)]) & (df_cat["Y_WORLD" < (dec-err)])]
            
            if len(match) > 1:
                print("More than 1 SExtractor source match found for coordinates ", ra, ",", dec)
                continue
            if len(match) == 0:
                print("No SExtractor source matches for coordinates ", ra, ",", dec)
                continue

            ps = re.compile("sci")
            m_sci = ps.match(m)
            pt = re.compile("tmpl")
            m_tmpl = pt.match(m)
            if m_sci:
                column_ending = "SCI"
            elif m_tmpl:
                column_ending = "TMPL"
            else:
                column_ending = "DIFF"

            df_cattmp[f"MAG_AUTO_{column_ending}"]     = match["MAG_AUTO"]
            df_cattmp[f"MAGERR_AUTO_{column_ending}"]  = match["MAGERR_AUTO"]
            df_cattmp[f"X_WORLD_{column_ending}"]      = match["X_WORLD"]
            df_cattmp[f"Y_WORLD_{column_ending}"]      = match["Y_WORLD"]
            df_cattmp[f"X_IMAGE_{column_ending}"]      = match["X_IMAGE"]
            df_cattmp[f"Y_IMAGE_{column_ending}"]      = match["Y_IMAGE"]
            df_cattmp[f"CLASS_STAR_{column_ending}"]   = match["CLASS_STAR"]
            df_cattmp[f"ELLIPTICITY_{column_ending}"]  = match["ELLIPTICITY"]
            df_cattmp[f"FWHM_WORLD_{column_ending}"]   = match["FWHM_WORLD"]
            df_cattmp[f"FWHM_IMAGE_{column_ending}"]   = match["FWHM_IMAGE"]
            df_cattmp[f"SPREAD_MODEL_{column_ending}"] = match["SPREAD_MODEL"]
            df_cattmp[f"FLAG_{column_ending}"]         = match["FLAG"]
        
        return df_cattmp

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
            "--cats_path_out",
            type=str,
            default="./cats",
            help="Path to SE catalogue outputs"
    )
    parser.add_argument(
            "--lc_path_out",
            type=str,
            default="./lc_files",
            help="Path to appended light curve files"
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

    os.makedirs(args.cats_path_out, exist_ok=True)  
    os.makedirs(args.lc_path_out, exist_ok=True)

    if args.test:
        print('-------------------------------------------')
        print('      TESTING FOR A SINGLE IMAGE SET       ')
        print('-------------------------------------------')

    if args.ccd:
        ccds = [args.ccd]
    else:
        ccds = range(1,62,1)

    for ccd in ccds:
        # Read in fits files
        sci_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.im.fits")
        diff_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.fits")
        tmpl_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.tmpl.fits")

        # Sort files in order of date
        sci_list.sort()
        diff_list.sort()
        tmpl_list.sort()

        if args.verbose:
            print(f'SCIENCE IMAGES, CCD {ccd}:')
            for ii, im in enumerate(sci_list):
                print(sci_list[ii])

            print(f'DIFFERENCE IMAGES, CCD {ccd}:')
            for ii, im in enumerate(diff_list):
                print(diff_list[ii])

            print(f'TEMPLATE IMAGES, CCD {ccd}:')
            for ii, im in enumerate(tmpl_list):
                print(tmpl_list[ii])
        
        # In case of empty CCD
        if len(sci_list) == 0:
            print(f"CCD {ccd} IS EMPTY")
            continue

        if args.test:
            sci_list = [sci_list[0]]  
            diff_list = [diff_list[0]]  
            tmpl_list = [tmpl_list[0]]  

            print('FIRST FILES IN LIST:')
            print(sci_list)
            print(diff_list)
            print(tmpl_list)

        # SE parameters
        savecats_dir = f"./cats/{args.field}/{ccd}"
        sextractor_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex"
        psfex_loc = "/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/psfex/3.21.1/bin/psfex"
        fwhm = 1.2           #default setting
        detect_minarea = 5   #default setting
        detect_thresh = 1.5  #default setting

        if args.verbose:
            print('SAVE CATALOG DIRECTORY: %s\n' % savecats_dir)

        # Run SE on science image
        # if args.verbose:
        #     print('=========================================')
        #     print('RUNNING SOURCE EXTRACTOR ON SCIENCE IMAGE')
        #     print('=========================================')
        # catending = f'{ccd}.sci'
        # _,_ = run_sextractor.run_sextractor(sci_list, sextractor_loc=sextractor_loc,
        #                                         psfex_loc=psfex_loc, savecats_dir=savecats_dir, 
        #                                         spreadmodel=True, catending=catending,
        #                                         fwhm=fwhm, detect_minarea=detect_minarea,
        #                                         detect_thresh=detect_thresh, ccd=ccd, field=args.field,
        #                                         diff_im=False, verbose=args.verbose)
        
        # Run SE on difference image
        # if args.verbose:
        #     print('============================================')
        #     print('RUNNING SOURCE EXTRACTOR ON DIFFERENCE IMAGE')
        #     print('============================================')
        # catending = f'{ccd}.diff'
        # _,_ = run_sextractor.run_sextractor(diff_list, sextractor_loc=sextractor_loc, 
        #                                         psfex_loc=psfex_loc, savecats_dir=savecats_dir,
        #                                         spreadmodel=False, catending=catending,
        #                                         fwhm=fwhm, detect_minarea=detect_minarea, 
        #                                         detect_thresh=detect_thresh, ccd=ccd, field=args.field,
        #                                         diff_im=True, verbose=args.verbose)

        # Run SE on template image
        # if args.verbose:
        #     print('==========================================')
        #     print('RUNNING SOURCE EXTRACTOR ON TEMPLATE IMAGE')
        #     print('==========================================')
        # catending = f'{ccd}.tmpl'
        # _,_ = run_sextractor.run_sextractor(tmpl_list, sextractor_loc=sextractor_loc, 
        #                                         psfex_loc=psfex_loc, savecats_dir=savecats_dir,
        #                                         spreadmodel=True, catending=catending,
        #                                         fwhm=fwhm, detect_minarea=detect_minarea, 
        #                                         detect_thresh=detect_thresh, ccd=ccd, field=args.field,
        #                                         diff_im=False, verbose=args.verbose)
        

        # Read in unforced diff light curve files pathnames 
        if args.verbose:
            print('=========================================================')
            print('MATCHING SOURCE EXTRACTOR SOURCES TO CANDIDATE DETECTIONS')
            print('=========================================================')
        
        lc_outdir = (f"./lc_files/{args.field}/{ccd}")
        if not os.path.exists(lc_outdir):
            os.makedirs(lc_outdir)

        difflc_files = glob.glob(f'../../web/web/sniff/{args.field}_tmpl/{ccd}/*/*.unforced.difflc.txt')        

        if args.test:
            difflc_files = [difflc_files[0]]
            print("TESTING ON A SINGLE CANDIDATE\n")

        if args.verbose:
            print(f'DIFFERENCE LIGHT CURVE FILES, CCD {ccd}:')
            for ii, f in enumerate(difflc_files):
                print(difflc_files[ii])

        for f in difflc_files:
            df = read_file(f)

            # Reading in candidate ID from file name, by finding the last group of digits in string
            p = re.compile(r'\d+')
            cand_id = p.findall(f)[-1]

            # Finding detection dates and converting them to YYMMDD format
            det_dates = df["dateobs"]
            for ii, d in enumerate(det_dates):
                det_dates[ii] = d.replace("-", "")[2:8]
            df["dateobs"] = det_dates

            if args.verbose:
                print('CANDIDATE ID: ', cand_id)
                print('DETECTION DATES & COORDS:')
                print(df[["dateobs", "ra", "dec"]])
            
            ### will have to convert coords at some stage idk which to what format though
            for ii, d in enumerate(det_dates):
                date = df["dateobs"][ii]
                ra = df["ra"][ii]
                dec = df["dec"][ii]
                filt = df["filt"][ii]

                match_cat_table = cat_match(date, ra, dec, filt)

                df_out = pd.merge(df, match_cat_table, by='id_column', how='left')      

            df.to_csv(f'{lc_outdir}/cand{cand_id}.unforced.difflc.app.txt')

    #   THINGS TO DO:
    #     READ IN UNFORCED DIFFLC FILES
    #     APPEND CAT DATA INTO DIFFLC FILE (SAVE AS NEW FILE)
    #         READ DETECTION DATE AND RA & DEC 
    #         MATCH WITH SOURCE IN SOURCE EXTRACTOR CATALOGUE
    #         PLACE DATA INTO CORRECT ROW AND NEW SE COLUMN
        
    #     CROSSMATCHING
    #         FOR EACH DETECTION RUN PAN-STARRS, GAIA, SIMBAD XMATCH
    #         APPEND INFORMATION TO DIFFLC FILE

    #     CREATE MASTERLIST 
    #     APPEND DIFFLC DATA/ METADATA TO MASTERLIST
    #         CAND ID; FIELD; RA; DEC; NO. DETECTIONS; NO. CONSECUTIVE DETECTIONS; NO. GOOD DETECTIONS; XMATCH; PATH; 


         
