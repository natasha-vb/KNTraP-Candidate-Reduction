import argparse
import glob
import os
import pandas as pd
import re
import ipdb

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Iterating over candidate filtering conditions")

    parser.add_argument(
                "--field",
                type=str,
                help="Selected field"
        )
    parser.add_argument(
            "--verbose", "--v",
            action="store_true",
            help="Making code more verbose"
    )
    args = parser.parse_args()

    # Source Extractor Filter Values
    ellipticity = '< 0.7'
    fwhm = ' < 2 * (seeing/0.263)'
    spread_model = '> -0.02 & < 0.02'

    # Grabbing masterlists from all field directories or one specified field
    if args.field:
        masterlists_field = glob.glob(f'./masterlist/{args.field}/*.allccds_xmatch.csv')
        if args.verbose:
            print('MASTERLISTS FOUND:')
            print(masterlists_field)
    else:
        masterlists_field = glob.glob(f'./masterlist/*/*.allccds_xmatch.csv')
        if args.verbose:
            print('MASTERLISTS FOUND:')
            print(masterlists_field)

    # Loop over field
    for m in masterlists_field:
        # Reading in masterlist
        mlist = pd.read_csv(m, sep=',')
        field = mlist['FIELD'][0]

        priority_outdir = (f'./masterlist/{field}/priority')
        if not os.path.exists(priority_outdir):
            os.makedirs(priority_outdir)
        
        # Sorting candidates into three groups; promising, potential, uninteresting
        m_promising = mlist[lambda mlist: (mlist.N_CONSECUTIVE_DETECTIONS_i >= 4) | (mlist.N_CONSECUTIVE_DETECTIONS_g >= 4) |
                                          (mlist.N_CONSECUTIVE_DETECTIONS_i_1h >= 4) | (mlist.N_CONSECUTIVE_DETECTIONS_g_1h >= 4)]

        m_potential = mlist[lambda mlist: (mlist.N_CONSECUTIVE_DETECTIONS_i < 4) & (mlist.N_CONSECUTIVE_DETECTIONS_i >= 2) |
                                          (mlist.N_CONSECUTIVE_DETECTIONS_i_1h < 4) & (mlist.N_CONSECUTIVE_DETECTIONS_i_1h >= 2) |
                                          (mlist.N_CONSECUTIVE_DETECTIONS_g < 4) & (mlist.N_CONSECUTIVE_DETECTIONS_g >= 2) | 
                                          (mlist.N_CONSECUTIVE_DETECTIONS_g_1h < 4) & (mlist.N_CONSECUTIVE_DETECTIONS_g_1h >= 2)]
        
        m_uninteresting = mlist[lambda mlist: (mlist.N_CONSECUTIVE_DETECTIONS_i < 2) | (mlist.N_CONSECUTIVE_DETECTIONS_g < 2) |
                                              (mlist.N_CONSECUTIVE_DETECTIONS_i_1h < 2) | (mlist.N_CONSECUTIVE_DETECTIONS_g_1h < 2) ]
        

        # Remove candidates with star-like object in template image
        m_promising = m_promising[~(m_promising['SPREAD_MODEL_TEMP'] > -0.002) & ~(m_promising['SPREAD_MODEL_TEMP'] < 0.002)]
        m_potential = m_potential[~(m_potential['SPREAD_MODEL_TEMP'] > -0.002) & ~(m_potential['SPREAD_MODEL_TEMP'] < 0.002)]

        # Linear fits to candidates and cutting on rising/ fading rates
        ### search for minima and maxima
        ### if one minima and one maxima: simple linear fit to see fading rate
        ### if two minima and one maxima: two linear fits for rise and fade
        ### if two maxima and one minima: two linear fits for fade and rise
        lc_files_path = m_promising['LC_PATH']
        for lc in lc_files_path:
            df = pd.read_csv(lc)
            

       ##################################################################################################################################
       #### SORT CANDIDATES INTO THREE GROUPS:
       #### PROMISING (MANY DATA POINTS, >4?)
       #### POTENTIAL (COULD BE INTERESTING, 2 < DATA POINTS < 4)
       #### UNINTERESTING (PROBABLY NOT ANYTHING, <2 DATA POINTS)

       #### FOR PROMISING AND POTENTIAL:
        #### CUT OUT SOURCES WITH A STAR LIKE OBJECT IN TEMPLATE IMAGE (VIA SPREAD MODEL)
        #### FIT LINEAR RISING/ FADING LINES
        #### IF FADING RATE IS REASONABLE FOR A KN OR AFTERGLOW, KEEP (~ 1 MAG/DAY FOR AFTERGLOW, ~0.3 MAG/DAY FOR KN) 