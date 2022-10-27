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
    spread_model = '> -0.2 & < 0.2'

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
        
        # Iterating over different filtering criteria 
        for i in range (2,5,1):
            ########################################################################
            mcut_i = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_i >= i]
            mcut_i = mcut_i.reset_index()   
            mcut_i_len = len(mcut_i)

            ############# put '#' in front of each line to make them comments
            text = """\ 
            # -------------------
            #SELECTION CRITERIA:
            #-------------------
            #ELLIPTICITY %s
            #FWHM %s
            #SPREAD MODEL %s
            #CONSECUTIVE DETECTIONS IN I BAND >= %s 
            #
            #--- NUMBER OF CANDIDATES FOUND: %s
            #
            {}""" % (ellipticity, fwhm, spread_model,i, mcut_i_len)

            with open(f'{priority_outdir}/i_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_i.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_i_len}')

            ########################################################################
            mcut_g = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_g >= i]
            mcut_g = mcut_g.reset_index()
            mcut_g_len = len(mcut_g)

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

            with open(f'{priority_outdir}/g_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_g.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN G BAND >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_g_len}')                

            ########################################################################
            mcut_i_1h = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_i_1h >= i]
            mcut_i_1h = mcut_i_1h.reset_index()
            mcut_i_1h_len = len(mcut_i_1h)

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

            with open(f'{priority_outdir}/i_1h_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_i_1h.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}')
                print(f'{mcut_i_1h_len}')                

            ########################################################################
            mcut_g_1h = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_g_1h >= i]
            mcut_g_1h = mcut_g_1h.reset_index()
            mcut_g_1h_len = len(mcut_g_1h)

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

            with open(f'{priority_outdir}/g_1h_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_g_1h.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN G BAND WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_g_1h_len}')                

            ########################################################################
            mcut_i_g = mlist[lambda mlist: (mlist.N_CONSECUTIVE_DETECTIONS_i >= i) | (mlist.N_CONSECUTIVE_DETECTIONS_g >= i)]
            mcut_i_g = mcut_i_g.reset_index()
            mcut_i_g_len = len(mcut_i_g)

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

            with open(f'{priority_outdir}/i_g_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_i_g.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND OR G BAND >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_i_g_len}')                

            ########################################################################
            mcut_i_g_1h = mlist[lambda mlist: (mlist.N_CONSECUTIVE_DETECTIONS_i_1h >= i) | (mlist.N_CONSECUTIVE_DETECTIONS_g_1h >= i)]
            mcut_i_g_1h = mcut_i_g_1h.reset_index()
            mcut_i_g_1h_len = len(mcut_i_g_1h)

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

            with open(f'{priority_outdir}/i_g_1h_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_i_g_1h.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN I BAND OR G BAND WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_i_g_1h_len}')
                
            ########################################################################
            mcut_ig = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_ig >= i]
            mcut_ig = mcut_ig.reset_index()
            mcut_ig_len = len(mcut_ig)

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

            with open(f'{priority_outdir}/ig_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_ig.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_ig_len}')                

            ########################################################################
            mcut_ig_1h = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_ig_1h >= i]
            mcut_ig_1h = mcut_ig_1h.reset_index()
            mcut_ig_1h_len = len(mcut_ig_1h)

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

            with open(f'{priority_outdir}/ig_1h_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_ig_1h.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN IN BOTH I AND G BANDS WITH ONE HOLE >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}')
                print(f'{mcut_ig_1h_len}')                

            ########################################################################
            mcut_ig_2h = mlist[lambda mlist: mlist.N_CONSECUTIVE_DETECTIONS_ig_2h >= i]
            mcut_ig_2h = mcut_ig_2h.reset_index()
            mcut_ig_2h_len = len(mcut_ig_2h)

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

            with open(f'{priority_outdir}/ig_2h_atleast{i}consec_{field}.csv', 'w') as fp:
                fp.write(text.format(mcut_ig_2h.to_csv(index=False)))

            if args.verbose:
                print(' ')
                print('-------------------------------------------------')
                print('CRITERIA:')
                print(f'NUMBER OF CONSECUTIVE DETECTIONS IN BOTH I AND G BANDS WITH TWO HOLES >= {i}')
                print(' ')
                print(f'NUMBER OF CANDIDATES FOUND IN FIELD {field}:')
                print(f'{mcut_ig_2h_len}')
                
        
        # Count number of candidates in each reduced masterlist for each CCD
        ccds = range(1,63,1)
        for ccd in ccds:
            mcut_list = glob.glob(f'{priority_outdir}/*consec_{field}.csv')
            
            print('----------------------------------------------------------------------------------------')
            print(f'NUMBER OF CANDIDATES FOR THE FOLLOWING SELECTION CRITERIA IN FIELD {field} CCD {ccd}:')

            if len(mcut_list) == 0:
                if args.verbose:
                    print(f'CCD {ccd} masterlist not found')

            else:
                for m in mcut_list:
                    m_df = pd.read_csv(m, sep=',', skiprows=[1,2,3,4,5,6,7,8,9,10]) # read comments as '#' <-- double check this

                    if len(m_df) > 1:
                        ipdb.set_trace()
                        m_ccd = m_df[m_df['CCD'] == ccd]
                        m_ccd_len = len(m_ccd)

                        p_ig = re.compile("ig_")
                        ig = p_ig.search(m)
                        
                        p_i_g = re.compile("i_g_")
                        i_g = p_i_g.search(m)

                        p_i = re.compile("i_")
                        i_ = p_i.search(m)

                        p_g = re.compile("g_")
                        g_ = p_g.search(m)

                        p_1h = re.compile("_1h")
                        _1h = p_1h.search(m)

                        p_2h = re.compile("_2h")
                        _2h = p_2h.search(m)

                        if ig:
                            band = 'i and g band'
                        elif i_g:
                            band = 'i or g band'
                        elif i_:
                            band = 'i band'
                        elif g_:
                            band = 'g band'
                        
                        if _1h:
                            hole = ' with one hole '
                            p_num = re.compile(r'\d')
                            num = p_num.findall(m)[1]
                        elif _2h:
                            hole = ' with two holes '
                            p_num = re.compile(r'\d')
                            num = p_num.findall(m)[1]
                        else:
                            hole = ' '
                            p_num = re.compile(r'\d')
                            num = p_num.findall(m)[0]

                        print(f'> {num} consecutive {band} detections{hole}: {m_ccd_len} ')

                    else:
                        if args.verbose:
                            print('No candidates found in masterlist:', m)
                    
            print('----------------------------------------------------------------------------------------')
