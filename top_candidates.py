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
        
        n_cands = len(mlist)
        print(' ')
        print('=================================================')
        print(f'FILTERING FOR FIELD {field}')
        print(' ')
        print(f'INITIAL NUMBER OF CANDIDATES: {n_cands}')

        ############################################################################
        # Filtering candidates:
        # With star-like objects in template image
        mlist = mlist[lambda mlist: mlist.TMPL_STAR_CHECK == True]

        n_cands = len(mlist)
        print(' ')
        print(f'NUMBER AFTER FILTERING CANDIDATES WITH STAR-LIKE OBJECTS IN TEMPLATE IMAGE: {n_cands}')

        # With kilonova-like rising and/or fading rates
        # mlist = mlist[lambda mlist: (mlist.RISE_i == True) | (mlist.FADE_i == True) |
        #                             (mlist.RISE_g == True) | (mlist.FADE_g == True)]
        
        # Requiring both rise and fade rates
        mlist = mlist[lambda mlist: (mlist.RATE_i == True) | (mlist.RATE_g == True)]
        
        n_cands = len(mlist)
        print(' ')
        print(f'NUMBER AFTER FILTERING CANDIDATES ON RISING/ FADING RATES: {n_cands}')
             
        # Filtering the top candidates, either primary or secondary
        # Primary candidates: >= 3 decections with 1 hole in i band
        # Secondary candidates >= 3 detections with 1 hole in g band

        ########################################################################
        ####################### PRIMARY CANDIDATES #############################
        mcut_i_1h = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_i_1h >= 3]
        mcut_i_1h = mcut_i_1h.reset_index()
        mcut_i_1h_len = len(mcut_i_1h)

        text = """\ 
        #-------------------
        #SELECTION CRITERIA:
        #-------------------
        #ELLIPTICITY %s
        #FWHM %s
        #SPREAD MODEL %s
        #CONSECUTIVE DETECTIONS IN I BAND WITH ONE HOLE >= %s 
        #
        #--- NUMBER OF CANDIDATES FOUND: %s
        #
        {}""" % (ellipticity, fwhm, spread_model,3, mcut_i_1h_len)

        with open(f'{priority_outdir}/primary_candidates_test_{field}.csv', 'w') as fp:
            fp.write(text.format(mcut_i_1h.to_csv(index=False)))

        if args.verbose:
            print(' ')
            print('-------------------------------------------------')
            print('CRITERIA:')
            print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND WITH ONE HOLE >= 3')
            print(' ')
            print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}')
            print(f'{mcut_i_1h_len}')                

        ########################################################################
        ###################### SECONDARY CANDIDATES ############################
        mcut_g_1h = mlist[lambda mlist: (mlist.N_CONSECUTIVE_DETECTIONS_g_1h >= 3) | (mlist.N_CONSECUTIVE_DETECTIONS_i_1h >= 2)]
        mcut_g_1h = mcut_g_1h.reset_index()
        mcut_g_1h_len = len(mcut_g_1h)

        text = """\ 
        #-------------------
        #SELECTION CRITERIA:
        #-------------------
        #ELLIPTICITY %s
        #FWHM %s
        #SPREAD MODEL %s
        #CONSECUTIVE DETECTIONS IN G BAND WITH ONE HOLE >= %s 
        #
        #--- NUMBER OF CANDIDATES FOUND: %s
        #
        {}""" % (ellipticity, fwhm, spread_model,3 , mcut_g_1h_len)

        with open(f'{priority_outdir}/secondary_candidates_test_{field}.csv', 'w') as fp:
            fp.write(text.format(mcut_g_1h.to_csv(index=False)))

        if args.verbose:
            print(' ')
            print('-------------------------------------------------')
            print('CRITERIA:')
            print(f'NUMBER OF CONSECUTIVE DETECTIONS IN G BAND WITH ONE HOLE >= 3 | I BAND WITH ONE HOLE >= 2')
            print(' ')
            print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
            print(f'{mcut_g_1h_len}')                