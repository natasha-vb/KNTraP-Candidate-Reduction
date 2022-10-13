import argparse
import glob
import ipdb 
import numpy as np
import os
import pandas as pd
from pathlib import Path
import re 
import statistics

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import astropy.io.ascii as ascii
from astropy.table import Table

from utils import cat_match
from utils import consecutive_count
from utils import crossmatch
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
            "--skip_se",
            action="store_true",
            help="Skip Source Extractor process"
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
        fwhm = 1.2           #default setting 1.2
        detect_minarea = 5   #default setting 5
        detect_thresh = 0.8  #default setting 1.5

        if args.verbose:
            print('SAVE CATALOG DIRECTORY: %s\n' % savecats_dir)

        if not args.skip_se:
            # Run SE on science image
            if args.verbose:
                print('=========================================')
                print('RUNNING SOURCE EXTRACTOR ON SCIENCE IMAGE')
                print('=========================================')
            catending = f'{ccd}.sci'
            _,_ = run_sextractor.run_sextractor(sci_list, sextractor_loc=sextractor_loc,
                                                    psfex_loc=psfex_loc, savecats_dir=savecats_dir, 
                                                    spreadmodel=True, catending=catending,
                                                    fwhm=fwhm, detect_minarea=detect_minarea,
                                                    detect_thresh=detect_thresh, ccd=ccd, field=args.field,
                                                    diff_im=False, verbose=args.verbose)
            
            # Run SE on difference image
            if args.verbose:
                print('============================================')
                print('RUNNING SOURCE EXTRACTOR ON DIFFERENCE IMAGE')
                print('============================================')
            catending = f'{ccd}.diff'
            _,_ = run_sextractor.run_sextractor(diff_list, sextractor_loc=sextractor_loc, 
                                                    psfex_loc=psfex_loc, savecats_dir=savecats_dir,
                                                    spreadmodel=False, catending=catending,
                                                    fwhm=fwhm, detect_minarea=detect_minarea, 
                                                    detect_thresh=detect_thresh, ccd=ccd, field=args.field,
                                                    diff_im=True, verbose=args.verbose)

            # Run SE on template image
            if args.verbose:
                print('==========================================')
                print('RUNNING SOURCE EXTRACTOR ON TEMPLATE IMAGE')
                print('==========================================')
            catending = f'{ccd}.tmpl'
            _,_ = run_sextractor.run_sextractor(tmpl_list, sextractor_loc=sextractor_loc, 
                                                    psfex_loc=psfex_loc, savecats_dir=savecats_dir,
                                                    spreadmodel=True, catending=catending,
                                                    fwhm=fwhm, detect_minarea=detect_minarea, 
                                                    detect_thresh=detect_thresh, ccd=ccd, field=args.field,
                                                    diff_im=False, verbose=args.verbose)
        
        # Read in unforced diff light curve files pathnames 
        if args.verbose:
            print('=========================================================')
            print('MATCHING CANDIDATE DETECTIONS TO SOURCE EXTRACTOR SOURCES')
            print('=========================================================')
        
        lc_outdir = (f"./lc_files/{args.field}/{ccd}")
        if not os.path.exists(lc_outdir):
            os.makedirs(lc_outdir)

        masterlist_outdir = (f'./masterlist/{args.field}')
        if not os.path.exists(masterlist_outdir):
            os.makedirs(masterlist_outdir)

        difflc_files = glob.glob(f'../../web/web/sniff/{args.field}_tmpl/{ccd}/*/*.unforced.difflc.txt')        

        if args.test:
            difflc_files = [difflc_files[0]]
            print("TESTING ON A SINGLE CANDIDATE\n")

        if args.verbose:
            print(f'DIFFERENCE LIGHT CURVE FILES, CCD {ccd}:')
            for ii, f in enumerate(difflc_files):
                print(difflc_files[ii])
        
        masterlist = pd.DataFrame()
        empty_lc_files = []

        for f in difflc_files:
            if len(f) > 1:
                df = read_file(f)

                # Reading in candidate ID from file name, by finding the last group of digits in string
                p = re.compile(r'\d+')
                cand_id = p.findall(f)[-1]

                # Finding detection dates and converting them to YYMMDD format
                det_dates = df["dateobs"].values 
                det_dates = [f"{d.replace('-','')[2:8]}" for d in df["dateobs"].values ]
                df['dateobs'] = det_dates
                df = df.sort_values(by="dateobs")

                # Converting ra and dec to degrees
                coo = SkyCoord(df["ra"].astype(str),
                               df["dec"].astype(str),
                               unit=(u.hourangle, u.deg))
                df["ra"] = coo.ra.degree
                df["dec"] = coo.dec.degree
                
                if args.verbose:
                    print('-----------------------------------------')
                    print('CANDIDATE ID: ', cand_id)
                    print('DETECTION DATES & COORDS:')
                    print(df[["dateobs", "ra", "dec"]])

                cat_matches = pd.DataFrame()
                for ii, d in enumerate(det_dates):
                    date = df["dateobs"][ii]
                    ra = df["ra"][ii]
                    dec = df["dec"][ii]
                    filt = df["filt"][ii]

                    # Matching detection coordinates to source in SE catalogs
                    match_cat_table = cat_match.cat_match(date, ra, dec, filt, field=args.field, ccd=ccd, verbose=args.verbose)

                    cat_matches = pd.concat([cat_matches,match_cat_table],sort=False)

            else:
                # Listing all empty light curve files, can be checked out later
                print("LIGHT CURVE FILE IS EMPTY: ", f)
                empty_lc_files.append(f)

            # Merging light curve (df) with matched SExtractor catalogue data (cat_matches)
            df_out = pd.merge(df, cat_matches, how='left', on=['dateobs','filt'])

            # Adding column for average seeing for each night
            dic_dateobs_assig = {'220212':1.125, '220213':1.425, '220214':1.225, '220215':1.15, '220216':1.075, '220217':0.95, 
                                 '220218':1.3, '220219':0.975, '220220':0.8, '220221':1.1, '220222':1.5}
            df_out["av_seeing"] = df_out.apply(lambda row: dic_dateobs_assig[row.dateobs], axis=1)

            # True/ False for a "good" detection
            df_out["good_detection"] = df_out.apply(lambda row: True if row["ELLIPTICITY_DIFF"] < 1.0 and
                                                                        row["FWHM_IMAGE_DIFF"] < 10  and      #2*(row["av_seeing"]/0.26)
                                                                        row["SPREAD_MODEL_DIFF"] > -0.5 and
                                                                        row["SPREAD_MODEL_DIFF"] < 0.5 else
                                                                        False, axis=1)

            if args.verbose:
                    print('GOOD DETECTIONS?')
                    print(df_out[["dateobs","filt","av_seeing","good_detection"]])
                    print('-----------------------------------------')

            app_lc_name = (f'cand{cand_id}.unforced.difflc.app.txt')
            df_out.to_csv(f'{lc_outdir}/{app_lc_name}')

            if args.verbose:
                print(f"APPENDED LIGHT CURVE FILE SAVED AS: {lc_outdir}/{app_lc_name}\n")

            # Calculating masterlist data 
            ra_ave = statistics.mean(df["ra"])
            dec_ave = statistics.mean(df["dec"])
            n_det = len(df_out.index)
            n_conseq_det = consecutive_count.consecutive_count(df_out, verbose=True)
            n_good_det = len(df_out[df_out["good_detection"] == True])

            # Placing data into temp masterlist
            masterlist_tmp = pd.DataFrame({"CAND_ID": [cand_id],
                                           "FIELD": [args.field],
                                           "CCD": [ccd],
                                           "RA_AVERAGE": [ra_ave],
                                           "DEC_AVERAGE": [dec_ave],
                                           "N_DETECTIONS": [n_det],
                                        #    "N_CONSECUTIVE_DETECTIONS": [n_conseq_det],
                                           "N_GOOD_DETECTIONS": [n_good_det],
                                           "LC_PATH": [f]})
            if args.verbose:
                print(f'CANDIDATE {cand_id} MASTERLIST METADATA:')
                print(masterlist_tmp)
                print('===================================================================\
==============================================================\n')

            # Putting temp masterlist data into ccd masterlist
            masterlist = masterlist.append(masterlist_tmp)
            del(masterlist_tmp)

        # Saving masterlist to csv 
        masterlist.to_csv(f'{masterlist_outdir}/masterlist_{args.field}_{ccd}.csv', index=False)

        if args.verbose:
            print('=====================')
            print("M A S T E R L I S T :")
            print('=====================')
            print(masterlist)
            print()
            print("EMPTY LIGHT CURVE FILES:")
            print(empty_lc_files)

    # Combining all ccd masterlists to make masterlist for field
    masterlist_list = glob.glob(f'{masterlist_outdir}/*')
    masterlist_allccds = pd.DataFrame()
    for i, m in enumerate(masterlist_list):
        ml = pd.read_csv(masterlist_list[i])
        masterlist_allccds = masterlist_allccds.append(ml)

    masterlist_allccds_path = (f'{masterlist_outdir}/masterlist_{args.field}_allccds.csv')
    masterlist_allccds.to_csv(masterlist_allccds_path, index=False)

    ### DO CROSSMATCHING FOR MASTERLIST_ALLCCDS 
    ml_file = pd.read_csv(masterlist_allccds_path)
    
    ml_xmatch = crossmatch.crossmatch(ml_file,verbose=True)
    ml_xmatch.to_csv(f'{masterlist_outdir}/masterlist_{args.field}_allccds_xmatch.csv')
    
    print('XMATCHED MASTERLIST COLUMNS:')
    print(ml_xmatch.columns)


### MAKE MASTERLIST COMPILING ALL FIELDS?