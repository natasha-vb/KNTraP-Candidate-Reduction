import argparse
import glob
import os
import pandas as pd

parser = argparse.ArgumentParser(description="Iterating over candidate filtering conditions")

parser.add_argument(
        "--verbose", "--v",
        action="store_true",
        help="Making code more verbose"
)
args = parser.parse_args()

# Grabbing masterlists from all field directories
masterlists_field = glob.glob(f'./*/*.allccds_xmatch.csv')

# Source Extractor Filter Values
ellipticity = '< 0.7'
fwhm = ' < 2 * (seeing/0.263)'
spread_model = '> -0.2 & < 0.2'

# Loop over field
for m in masterlists_field:
    # Reading in masterlist
    mlist = pd.read_csv(m, sep=',')
    field = mlist['FIELD'][0]

    priority_outdir = (f'./masterlist/{field}/priority')
    if not os.path.exists(priority_outdir):
        os.makedirs(priority_outdir)
    
    
    ######### ITERATING OVER DIFFERENT CONDITIONS SOMEHOW??????????????????????????????????????????????????????????
    for i in range (2,5,1):
        
        # Initial field (sum of all CCDs) sum values for each criteria
        i_sum = 0
        g_sum = 0
        i_1h_sum = 0 
        g_1h_sum = 0
        i_g_sum = 0
        i_g_1h_sum = 0 
        ig_sum = 0
        ig_1h_sum = 0 
        ig_2h_sum = 0

        # Loop over ccds within field
        ccds = range(1,63,1)

        for ccd in ccds:

            masterlist_ccd = glob.glob(f'./{field}/*_ccd{ccd}.csv')
            mlist_ccd = pd.read_csv(m, sep=',')

            ########################################################################
            mcut_i = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_i >= i]
            mcut_i = mcut_i.reset_index()   
            mcut_i_len = len(mcut_i)
            i_sum += mcut_i_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN I BAND >= %s 
            
            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_i_len)

            with open(f'{priority_outdir}/i_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_i.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_i_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_g = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_g >= i]
            mcut_g = mcut_g.reset_index()
            mcut_g_len = len(mcut_g)
            g_sum += mcut_g_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN G BAND >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_g_len)

            with open(f'{priority_outdir}/g_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_g.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN G BAND >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_g_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_i_1h = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_i_1h >= i]
            mcut_i_1h = mcut_i_1h.reset_index()
            mcut_i_1h_len = len(mcut_i_1h)
            i_1h_sum += mcut_i_1h_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN I BAND WITH ONE HOLE >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_i_1h_len)

            with open(f'{priority_outdir}/i_1h_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_i_1h.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_i_1h_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_g_1h = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_g_1h >= i]
            mcut_g_1h = mcut_g_1h.reset_index()
            mcut_g_1h_len = len(mcut_g_1h)
            g_1h_sum += mcut_g_1h_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN G BAND WITH ONE HOLE >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_g_1h_len)

            with open(f'{priority_outdir}/g_1h_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_g_1h.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN G BAND WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_g_1h_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_i_g = mlist_ccd[lambda mlist_ccd: (mlist_ccd.N_CONSECUTIVE_DETECTIONS_i >= i) | (mlist_ccd.N_CONSECUTIVE_DETECTIONS_g >= i)]
            mcut_i_g = mcut_i_g.reset_index()
            mcut_i_g_len = len(mcut_i_g)
            i_g_sum += mcut_i_g_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN I BAND OR G BAND >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_i_g_len)

            with open(f'{priority_outdir}/i_g_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_i_g.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND OR G BAND >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_i_g_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_i_g_1h = mlist_ccd[lambda mlist_ccd: (mlist_ccd.N_CONSECUTIVE_DETECTIONS_i_1h >= i) | (mlist_ccd.N_CONSECUTIVE_DETECTIONS_g_1h >= i)]
            mcut_i_g_1h = mcut_i_g_1h.reset_index()
            mcut_i_g_1h_len = len(mcut_i_g_1h)
            i_g_1h_sum += mcut_i_g_1h_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN I BAND OR G BAND WITH ONE HOLE >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_i_g_1h_len)

            with open(f'{priority_outdir}/i_g_1h_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_i_g_1h.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND OR G BAND WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_i_g_1h_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_ig = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_ig >= i]
            mcut_ig = mcut_ig.reset_index()
            mcut_ig_len = len(mcut_ig)
            ig_sum += mcut_ig_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_ig_len)

            with open(f'{priority_outdir}/ig_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_ig.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_ig_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_ig_1h = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_ig_1h >= i]
            mcut_ig_1h = mcut_ig_1h.reset_index()
            mcut_ig_1h_len = len(mcut_ig_1h)
            ig_1h_sum += mcut_ig_1h_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS WITH ONE HOLE >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_ig_1h_len)

            with open(f'{priority_outdir}/ig_1h_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_ig_1h.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN IN BOTH I AND G BANDS WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_ig_1h_len}')
                print('-------------------------------------------------')
                print(' ')

            ########################################################################
            mcut_ig_2h = mlist_ccd[lambda mlist_ccd: mlist_ccd.N_CONSECUTIVE_DETECTIONS_ig_2h >= i]
            mcut_ig_2h = mcut_ig_2h.reset_index()
            mcut_ig_2h_len = len(mcut_ig_2h)
            ig_2h_sum += mcut_ig_2h_len

            text = """\ 
            -------------------
            SELECTION CRITERIA:
            -------------------
            ELLIPTICITY %s
            FWHM %s
            SPREAD MODEL %s
            CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS WITH TWO HOLES >= %s 

            --- NUMBER OF CANDIDATES FOUND: %s

            {}""" % (ellipticity, fwhm, spread_model,i, mcut_i_len)

            with open(f'{priority_outdir}/ig_2h_atleast{i}consec_{field}_ccd{ccd}.csv', 'w') as fp:
                fp.write(text.format(mcut_ig_2h.to_csv(index=False)))

            if args.verbose:
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS WITH TWO HOLES >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} CCD {ccd}:')
                print(f'{mcut_ig_2h_len}')
                print('-------------------------------------------------')
                print(' ')
        
    # Sum of all CCDs for this condition 
        print('=================================================================')
        print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field} FOR EACH CRITERIA:')
        print('=================================================================')
        print(f'I BAND >= {i}: {i_sum}')
        print(f'G BAND >= {i}: {g_sum}')
        print(f'I BAND 1 HOLE >= {i_1h_sum}')
        print(f'G BAND 1 HOLE >= {g_1h_sum}')
        print(f'I OR G BAND >= {i_g_sum}')
        print(f'I OR G BAND 1 HOLE >= {i_g_1h_sum}')
        print(f'I AND G BANDS >= {ig_sum}')
        print(f'I AND G BANDS 1 HOLE >= {ig_1h_sum}')
        print(f'I AND G BANDS 2 HOLES >= {ig_2h_sum}')
        print(' ')