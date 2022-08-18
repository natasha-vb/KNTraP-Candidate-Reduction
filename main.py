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
from astropy.coordinates import SkyCoord
from astropy import units as u

from utils import run_sextractor

def cat_match(date, ra, dec, filt, field='257A', ccd='1'):
        match_list = glob.glob(f'./cats/{field}/{ccd}/*.{date}.*_{filt}_*.cat')
        df_cattmp = pd.DataFrame()

        df_cattmp["dateobs"] = [f"{date}"]
        df_cattmp["filt"]    = [f"{filt}"]

        for m in match_list:
            cat = ascii.read(m)
            df_cat = pd.DataFrame(cat.as_array())

            # Matching detection coordinates to SE catalogue
            coords_det = SkyCoord(ra=[ra], dec=[dec],unit='deg')
            coords_cat = SkyCoord(ra=df_cat["X_WORLD"], dec=df_cat["Y_WORLD"],unit='deg')

            idx, d2d, d3d = coords_det.match_to_catalog_3d(coords_cat)

            # Separation constraint (~ 1 arcsec) ### might not match with only 1 arcsec, try 2 arcsecs
            sep_constraint = d2d < (2 * u.arcsec)

            df_cat_matched = df_cat.iloc[idx[sep_constraint]]
            
            if df_cat_matched.empty:
                df_cat_matched[["MAG_AUTO", "MAGERR_AUTO", "X_WORLD", "Y_WORLD", 
                                "X_IMAGE", "Y_IMAGE", "CLASS_STAR", "ELLIPTICITY",
                                "FWHM_WORLD", "FWHM_IMAGE", "SPREAD_MODEL", "FLAGS"]] = [" "]

            df_cat_matched = df_cat_matched.reset_index(drop=False)

            ps = re.compile("sci")
            m_sci = ps.search(m)
            pt = re.compile("tmpl")
            m_tmpl = pt.search(m)
            if m_sci:
                column_ending = "SCI"
            elif m_tmpl:
                column_ending = "TMPL"
            else:
                column_ending = "DIFF"
            
            df_cattmp[f"MAG_AUTO_{column_ending}"]     = df_cat_matched["MAG_AUTO"]
            df_cattmp[f"MAGERR_AUTO_{column_ending}"]  = df_cat_matched["MAGERR_AUTO"]
            df_cattmp[f"X_WORLD_{column_ending}"]      = df_cat_matched["X_WORLD"]
            df_cattmp[f"Y_WORLD_{column_ending}"]      = df_cat_matched["Y_WORLD"]
            df_cattmp[f"X_IMAGE_{column_ending}"]      = df_cat_matched["X_IMAGE"]
            df_cattmp[f"Y_IMAGE_{column_ending}"]      = df_cat_matched["Y_IMAGE"]
            df_cattmp[f"CLASS_STAR_{column_ending}"]   = df_cat_matched["CLASS_STAR"]
            df_cattmp[f"ELLIPTICITY_{column_ending}"]  = df_cat_matched["ELLIPTICITY"]
            df_cattmp[f"FWHM_WORLD_{column_ending}"]   = df_cat_matched["FWHM_WORLD"]
            df_cattmp[f"FWHM_IMAGE_{column_ending}"]   = df_cat_matched["FWHM_IMAGE"]
            df_cattmp[f"SPREAD_MODEL_{column_ending}"] = df_cat_matched["SPREAD_MODEL"]
            df_cattmp[f"FLAGS_{column_ending}"]         = df_cat_matched["FLAGS"]
        
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
            print('MATCHING CANDIDATE DETECTIONS TO SOURCE EXTRACTOR SOURCES')
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
            # look into datetime
            det_dates = df["dateobs"].values 
            for ii, d in enumerate(det_dates):
                det_dates[ii] = d.replace("-", "")[2:8]
            df["dateobs"] = det_dates
            
            # Converting ra and dec to degrees
            coo = SkyCoord(df["ra"].astype(str),
                           df["dec"].astype(str),
                           unit=(u.hourangle, u.deg))
            df["ra"] = coo.ra.degree
            df["dec"] = coo.dec.degree
                        
            if args.verbose:
                print('CANDIDATE ID: ', cand_id)
                print('DETECTION DATES & COORDS:')
                print(df[["dateobs", "ra", "dec"]])
            
            for ii, d in enumerate(det_dates):
                date = df["dateobs"][ii]
                ra = df["ra"][ii]
                dec = df["dec"][ii]
                filt = df["filt"][ii]

                match_cat_table = cat_match(date, ra, dec, filt, field=args.field, ccd=ccd)

                df_out = pd.merge(df, match_cat_table, how='left', on=['dateobs','filt'])  ### merge by columns dateobs, filt

            df_out.to_csv(f'{lc_outdir}/cand{cand_id}.unforced.difflc.app.txt')

    

    #   THINGS TO DO:
    #     READ IN UNFORCED DIFFLC FILES
    #     APPEND CAT DATA INTO DIFFLC FILE (SAVE AS NEW FILE)
    #         READ DETECTION DATE AND RA & DEC 
    #         MATCH WITH SOURCE IN SOURCE EXTRACTOR CATALOGUE
    #         PLACE DATA INTO CORRECT ROW AND NEW SE COLUMN

    #     CREATE MASTERLIST 
    #     APPEND DIFFLC DATA/ METADATA TO MASTERLIST
    #         CAND ID; FIELD; RA; DEC; NO. DETECTIONS; NO. CONSECUTIVE DETECTIONS; NO. GOOD DETECTIONS; XMATCH; PATH; 

    #     CROSSMATCHING
    #         FOR EACH DETECTION RUN PAN-STARRS, GAIA, SIMBAD XMATCH
    #         APPEND INFORMATION TO MASTERLIST

         
