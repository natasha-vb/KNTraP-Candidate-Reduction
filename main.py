import argparse
import glob
import ipdb 
import numpy as np
import os
import pandas as pd
from pathlib import Path
import re 
import statistics
import time

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import astropy.io.ascii as ascii
from astropy.table import Table

from utils import cat_match
from utils import consecutive_count
from utils import crossmatch
from utils import mag_rates
from utils import run_sextractor
from utils import grab_seeing

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
            "--debug",
            action="store_true",
            help="Produce more print statements for debugging"
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
        ccds = range(1,63,1)

    for ccd in ccds:
        # Read in fits files
        sci_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.im.fits")
        diff_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.fits")
        tmpl_list = glob.glob(f"../../workspace/{args.field}_tmpl/{ccd}/*.diff.tmpl.fits") # First night templates

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
        sextractor_loc = "/fred/oz100/containers/commands/sex"
        psfex_loc = "/fred/oz100/containers/commands/psfex"
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
            start_time = time.time()
            catending = f'{ccd}.sci'
            _,_ = run_sextractor.run_sextractor(sci_list, sextractor_loc=sextractor_loc,
                                                    psfex_loc=psfex_loc, savecats_dir=savecats_dir, 
                                                    spreadmodel=True, catending=catending,
                                                    fwhm=fwhm, detect_minarea=detect_minarea,
                                                    detect_thresh=detect_thresh, ccd=ccd, field=args.field,
                                                    diff_im=False, verbose=args.verbose)
            end_time = time.time()
            time_diff = end_time - start_time
            if args.verbose:
                print('')
                print('-------------------------------------------------------------------------')
                print(f'TIME TAKEN FOR SOURCE EXTRACTOR AND PSFEx ON SCI IMAGE: {time_diff} seconds')
                print('-------------------------------------------------------------------------')

            # Run SE on difference image
            if args.verbose:
                print('============================================')
                print('RUNNING SOURCE EXTRACTOR ON DIFFERENCE IMAGE')
                print('============================================')
            start_time = time.time()
            catending = f'{ccd}.diff'
            _,_ = run_sextractor.run_sextractor(diff_list, sextractor_loc=sextractor_loc, 
                                                    psfex_loc=psfex_loc, savecats_dir=savecats_dir,
                                                    spreadmodel=False, catending=catending,
                                                    fwhm=fwhm, detect_minarea=detect_minarea, 
                                                    detect_thresh=detect_thresh, ccd=ccd, field=args.field,
                                                    diff_im=True, verbose=args.verbose)
            end_time = time.time()
            time_diff = end_time - start_time
            if args.verbose:
                print('')
                print('-------------------------------------------------------------------------')
                print(f'TIME TAKEN FOR SOURCE EXTRACTOR AND PSFEx ON DIFF IMAGE: {time_diff} seconds')
                print('-------------------------------------------------------------------------')

            # Run SE on template image
            if args.verbose:
                print('==========================================')
                print('RUNNING SOURCE EXTRACTOR ON TEMPLATE IMAGE')
                print('==========================================')
            start_time = time.time()
            catending = f'{ccd}.tmpl'
            _,_ = run_sextractor.run_sextractor(tmpl_list, sextractor_loc=sextractor_loc, 
                                                    psfex_loc=psfex_loc, savecats_dir=savecats_dir,
                                                    spreadmodel=True, catending=catending,
                                                    fwhm=fwhm, detect_minarea=detect_minarea, 
                                                    detect_thresh=detect_thresh, ccd=ccd, field=args.field,
                                                    diff_im=False, verbose=args.verbose)
            end_time = time.time()
            time_diff = end_time - start_time
            if args.verbose:
                print('')
                print('-------------------------------------------------------------------------')
                print(f'TIME TAKEN FOR SOURCE EXTRACTOR AND PSFEx ON TMPL IMAGE: {time_diff} seconds')
                print('-------------------------------------------------------------------------')

        # Read in unforced diff light curve files pathnames 
        if args.verbose:
            print('=========================================================')
            print('MATCHING CANDIDATE DETECTIONS TO SOURCE EXTRACTOR SOURCES')
            print('=========================================================')
        
        lc_outdir = (f"./lc_files/{args.field}/{ccd}")
        if not os.path.exists(lc_outdir):
            os.makedirs(lc_outdir)
        
        logs_outdir = (f'./logs/{args.field}')
        if not os.path.exists(logs_outdir):
            os.makedirs(logs_outdir)

        masterlist_outdir = (f'./masterlist/{args.field}')
        if not os.path.exists(masterlist_outdir):
            os.makedirs(masterlist_outdir)
        
        priority_outdir = (f'./masterlist/{args.field}/priority')
        if not os.path.exists(priority_outdir):
            os.makedirs(priority_outdir)

        difflc_files = glob.glob(f'../../web/web/sniff/{args.field}_tmpl/{ccd}/*/*.unforced.difflc.txt')        

        if args.test:
            difflc_files = [difflc_files[0]]
            print("TESTING ON A SINGLE CANDIDATE\n")

        if args.verbose:
            print(f'DIFFERENCE LIGHT CURVE FILES, CCD {ccd}:')
            for ii, f in enumerate(difflc_files):
                print(difflc_files[ii])
                print(' ')
        
        masterlist = pd.DataFrame()
        empty_lc_files = []
        unread_lc_files = []

        for f in difflc_files:
            if len(f) > 1:
                df = read_file(f)

                if len(df) > 1:
                    # Reading in candidate ID from file name, by finding the last group of digits in string
                    p = re.compile(r'\d+')
                    cand_id = p.findall(f)[-1]

                    # Finding detection dates and converting them to YYMMDD format
                    det_dates = df["dateobs"].values 
                    det_dates = [f"{d.replace('-','')[2:8]}" for d in df["dateobs"].values]
                    df['dateobs'] = det_dates
                    df = df.sort_values(by="dateobs")

                    # Converting ra and dec to degrees
                    coo = SkyCoord(df["ra"].astype(str),
                                   df["dec"].astype(str),
                                unit=(u.hourangle, u.deg))
                    df["ra"] = coo.ra.degree
                    df["dec"] = coo.dec.degree
                    
                    # if args.verbose:
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

                        # For deep field, use MJD date for SE catalog matching
                        datemjd = np.round(df['MJD'][ii], 0)
                        datemjd = int(datemjd)

                        # Matching detection coordinates to source in SE catalogs
                        match_cat_table = cat_match.cat_match(datemjd, date, ra, dec, filt, field=args.field, ccd=ccd, verbose=args.verbose)
                        cat_matches = pd.concat([cat_matches,match_cat_table],sort=False)

                    # Merging light curve (df) with matched SExtractor catalogue data (cat_matches)
                    df_out = pd.merge(df, cat_matches, how='left', on=['dateobs','filt'])

                    # Adding column for seeing for each night
                    df_seeing = grab_seeing.grab_seeing(df,args.field,ccd, debug=args.debug, verbose=args.verbose)
                    df_out = pd.merge(df_out,df_seeing, how='left', on=['dateobs', 'filt'])
                    
                    # True/ False for a "good" detection
                    df_out["good_detection"] = df_out.apply(lambda row: True if row["ELLIPTICITY_DIFF"] < 0.7 and 
                                                                                row["FWHM_IMAGE_DIFF"] < 2*(row["seeing"]/0.263) and 
                                                                                row["SPREAD_MODEL_DIFF"] > -0.02 and
                                                                                row["SPREAD_MODEL_DIFF"] < 0.02 else
                                                                                False, axis=1)
                    # df_out["good_detection"] = True

                    if args.verbose:
                            print('GOOD DETECTIONS?')
                            print(df_out[["dateobs","filt","seeing","good_detection"]])
                            print('-----------------------------------------')
                    
                    if args.debug:
                        print(' ')
                        print('=================================================')
                        print('DF OUT CHECK')
                        print(df_out)
                        for cols in df_out.columns:
                            print(cols)
                        print('=================================================')
                        print(' ')

                    # Check for star-like objects in template image
                    # True = star-like object in template image
                    df_out['tmpl_star_check'] = df_out.apply(lambda row: True if row['SPREAD_MODEL_TMPL'] < 0.002 and
                                                                                 row['SPREAD_MODEL_TMPL'] > -0.002  else
                                                                                 False, axis=1)
                    
                    # First and last detections, and in each bands
                    first_det = np.min(df_out['MJD'])
                    last_det = np.max(df_out['MJD'])
                    
                    # Calculate peak magnitude
                    mag_peak_mjd  = df_out.iloc[np.where(df_out['m'] == np.min(df_out['m']))]['MJD'].iloc[0]
                    mag_faint_mjd = df_out.iloc[np.where(df_out['m'] == np.max(df_out['m']))]['MJD'].iloc[0]
                    
                    if len(df_out[df_out['filt'] == 'i']) != 0:
                        mag_peak_i = min(df_out['m'][df_out['filt'] == 'i'])
                        mag_faint_i = max(df_out['m'][df_out['filt'] == 'i'])
                        first_det_i = np.min(df_out['MJD'][df_out['filt']=='i'])
                        last_det_i = np.max(df_out['MJD'][df_out['filt']=='i'])
                    else:
                        mag_peak_i  = np.NaN 
                        mag_faint_i = np.NaN
                        first_det_i = np.NaN
                        last_det_i  = np.NaN
                        
                    if len(df_out[df_out['filt'] == 'g']) != 0:    
                        mag_peak_g = min(df_out['m'][df_out['filt'] == 'g'])
                        mag_faint_g = max(df_out['m'][df_out['filt'] == 'g'])
                        first_det_g = np.min(df_out['MJD'][df_out['filt']=='g'])
                        last_det_g = np.max(df_out['MJD'][df_out['filt']=='g'])
                    else:
                        mag_peak_g  = np.NaN 
                        mag_faint_g = np.NaN
                        first_det_g = np.NaN
                        last_det_g  = np.NaN              
                    
                    # Calculate magnitude changes per day
                    df_alpha = mag_rates.mag_rates(df_out, verbose=args.verbose)
                    df_out = pd.merge(df_out,df_alpha, how='left', on=['dateobs', 'filt'])

                    # Calculate magnitude SNR 
                    df_out['mag_SNR'] = df_out['m'].replace('-', np.NaN).astype(float) / df_out['dm'].replace('-', np.NaN).astype(float)

                    app_lc_name = (f'cand{cand_id}.unforced.difflc.app.txt')
                    df_out.to_csv(f'{lc_outdir}/{app_lc_name}',index=False)

                    if args.verbose:
                        print(f"APPENDED LIGHT CURVE FILE SAVED AS: {lc_outdir}/{app_lc_name}\n")

                    # Calculating masterlist data 
                    ra_ave = statistics.mean(df["ra"])
                    dec_ave = statistics.mean(df["dec"])

                    x_image_data = df_out[~df_out['X_IMAGE_DIFF'].isnull()]['X_IMAGE_DIFF']
                    y_image_data = df_out[~df_out['Y_IMAGE_DIFF'].isnull()]['Y_IMAGE_DIFF']
                    if len(x_image_data) > 0:
                        x_image_ave = statistics.mean(x_image_data)
                    else:
                        x_image_ave = np.NaN
                    if len(y_image_data) > 0:
                        y_image_ave = statistics.mean(y_image_data)
                    else:
                        y_image_ave = np.NaN

                    tmpl_star_check = (df_out['tmpl_star_check'] == True).any()
                    n_det = len(df_out.index)
                    n_conseq_det = consecutive_count.consecutive_count(df_out, verbose=args.verbose)
                    n_good_det = len(df_out[df_out["good_detection"] == True])

                    # Checking for KN-like rising/ fading rates (-ve means rising, +ve means fading)
                    df_out['alpha_i'] = df_out['alpha_i'].apply(lambda x: float(x))
                    df_out['alpha_g'] = df_out['alpha_g'].apply(lambda x: float(x))

                    i_rise = (df_out['alpha_i'] < -1).any()
                    i_fade = (df_out['alpha_i'] > 0.3).any()
                    g_rise = (df_out['alpha_g'] < -1).any()
                    g_fade = (df_out['alpha_g'] > 0.3).any()

                    # Checking for both rise and fae
                    if i_rise == True & i_fade == True:
                        i_rate = True
                    else:
                        i_rate = False
                    
                    if g_rise == True & g_fade == True:
                        g_rate = True
                    else:
                        g_rate = False
                    
                    if args.debug:
                        print('RATES:')
                        print('i rise =', i_rise)
                        print('i fade = ', i_fade)
                        print('i rate = ', i_rate)
                        print(' ')
                        print('g rise =', g_rise)
                        print('g fade = ', g_fade)
                        print('g_rate = ', g_rate)

                    i_pos = (df_out['alpha_i'].dropna() > 0)
                    g_pos = (df_out['alpha_g'].dropna() > 0)
                    i_inflections = (i_pos & (i_pos != i_pos.shift(1))).sum()
                    g_inflections = (g_pos & (g_pos != g_pos.shift(1))).sum()

                    # Placing data into temp masterlist
                    masterlist_tmp = pd.DataFrame({"CAND_ID": [cand_id],
                                                "FIELD": [args.field],
                                                "CCD": [ccd],
                                                "RA_AVERAGE": [ra_ave],
                                                "DEC_AVERAGE": [dec_ave],
                                                "X_IMAGE": [x_image_ave],
                                                "Y_IMAGE": [y_image_ave],
                                                "MAG_PEAK_i": [mag_peak_i],
                                                "MAG_PEAK_g": [mag_peak_g],
                                                "MAG_PEAK_MJD": [mag_peak_mjd],
                                                "MAG_FAINT_i": [mag_faint_i],
                                                "MAG_FAINT_g": [mag_faint_g],
                                                "MAG_FAINT_MJD": [mag_faint_mjd],
                                                "FIRST_DET": [first_det],
                                                "LAST_DET": [last_det],
                                                "FIRST_DET_i": [first_det_i],
                                                "LAST_DET_i": [last_det_i],
                                                "FIRST_DET_g": [first_det_g],
                                                "LAST_DET_g": [last_det_g],
                                                "TMPL_STAR_CHECK": [tmpl_star_check],
                                                "N_DETECTIONS": [n_det],
                                                "N_GOOD_DETECTIONS": [n_good_det],
                                                "N_CONSECUTIVE_DETECTIONS_i": n_conseq_det['i'],
                                                "N_CONSECUTIVE_DETECTIONS_i_1h": n_conseq_det['i_1h'],
                                                "N_CONSECUTIVE_DETECTIONS_g": n_conseq_det['g'],
                                                "N_CONSECUTIVE_DETECTIONS_g_1h": n_conseq_det['g_1h'],
                                                "N_CONSECUTIVE_DETECTIONS_ig": n_conseq_det['ig'],
                                                "N_CONSECUTIVE_DETECTIONS_ig_1h": n_conseq_det['ig_1h'],
                                                "N_CONSECUTIVE_DETECTIONS_ig_2h": n_conseq_det['ig_2h'],
                                                "RATE_i": [i_rate],
                                                "RATE_g": [g_rate],
                                                "RISE_i": [i_rise],
                                                "FADE_i": [i_fade],
                                                "RISE_g": [g_rise],
                                                "FADE_g": [g_fade],
                                                "N_INFLECTIONS_i": [i_inflections],
                                                "N_INFLECTIONS_g": [g_inflections],
                                                "LC_PATH": [f]})
                    if args.verbose:
                        print('')
                        print(f'CANDIDATE {cand_id} MASTERLIST METADATA:')
                        print(masterlist_tmp)
                        print('===================================================================\
=========================================================================\n')
                        
                    if args.debug:
                        print('MASTERLIST COLUMNS:')
                        for col in masterlist_tmp.columns:
                            print(col)

                    # Putting temp masterlist data into ccd masterlist
                    masterlist = masterlist.append(masterlist_tmp, sort=False)
                    del(masterlist_tmp)

            else:
                # Listing all empty light curve files, can be checked out later
                print("LIGHT CURVE FILE IS EMPTY: ", f)
                empty_lc_files.append(f)

        # Saving masterlist to csv 
        masterlist.to_csv(f'{masterlist_outdir}/masterlist_{args.field}_ccd{ccd}.csv', index=False) 

        # Saving empty and unreadable light curves to csv
        empty_lc_df = pd.DataFrame(empty_lc_files, columns=['filename'])
        empty_lc_df.to_csv(f'{logs_outdir}/empty_lc_files_{args.field}_ccd{ccd}.csv',index=False)

        unread_lc_df = pd.DataFrame(unread_lc_files, columns=['filename'])
        unread_lc_df.to_csv(f'{logs_outdir}/unread_lc_files_{args.field}_ccd{ccd}.csv', index=False)

        if args.verbose:
            print('=====================')
            print("M A S T E R L I S T :")
            print('=====================')
            print(masterlist)
            print()
            print("EMPTY LIGHT CURVE FILES:")
            print(empty_lc_files)

    # Combining all ccd masterlists to make masterlist for field
    masterlist_list = glob.glob(f'{masterlist_outdir}/*{args.field}_*.csv')
    masterlist_allccds = pd.DataFrame()
    for i, m in enumerate(masterlist_list):
        try:
            ml = pd.read_csv(masterlist_list[i])
            masterlist_allccds = masterlist_allccds.append(ml,sort=False)
        except:
            print(f'Masterlist empty or corrupted: masterlist_{args.field}_ccd{ccd}.csv')

    masterlist_allccds = masterlist_allccds.sort_values(by = ['CCD', 'CAND_ID'] )

    masterlist_allccds_path = (f'{masterlist_outdir}/masterlist_{args.field}.allccds.csv')
    masterlist_allccds.to_csv(masterlist_allccds_path, index=False)