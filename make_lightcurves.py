import argparse
import glob 
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import ipdb 

def limiting_mag(df):
    df['limiting_mag'] = 0.0

    for ii, row in unflc_df.iterrows():
        if row['flux_c'] >= 0:
            df['limiting_mag'][ii] = -2.5*(np.log10(row['flux_c'] + 3*(row['dflux_c']))) + row['ZPTMAG_c']
        else:
            df['limiting_mag'][ii] = -2.5*(np.log10(3*(row['dflux_c']))) + row['ZPTMAG_c']

    return df


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Source Extractor to filter transient candidates")
    parser.add_argument(
            "--field",
            type=str,
            help="Selected field"
    )
    parser.add_argument(
            "--top_cands",
            action="store_true",
            help="Create light curves for only top candidates"

    )
    args = parser.parse_args()

    matplotlib.use('Agg') 

    print(' ')
    print('======================================')
    print('MAKING LIGHT CURVES FOR TOP CANDIDATES')
    print('======================================')
    print(' ')

    # Grab all masterlists of filtered candidates 
    if args.top_cands:
        top = '*_candidates'
    else:
        top = ''

    if args.field:
        filtered_mlists = glob.glob(f'./masterlist/{args.field}/priority/{top}*.csv')
    else:
        filtered_mlists = glob.glob(f'./masterlist/*/priority/{top}*.csv')

    for f in filtered_mlists:

        # Setting up directory to save light curves. Directory name is the filtering criteria parameters
        if args.field:
            field = args.field
        else:
            field = f.split('_')[-1].split('.')[0]

        lc_dir_name = f.split('/')[-1].replace('.csv','')
        lc_outdir = (f'./lc_files/{field}/filtered_candidates/{lc_dir_name}')

        if not os.path.exists(lc_outdir):
            os.makedirs(lc_outdir)

        print(f'Light curve directory: {lc_outdir}')

        # Read in masterlist
        df = pd.read_csv(f, sep=',', comment='#', header=11, skipinitialspace=True)

        # Iterate over candidates within masterlist 
        for i, cand in df.iterrows():

            cand_id = cand['CAND_ID']
            ccd = cand['CCD']
            
            print('------------------------------')
            print(f'CANDIDATE ID: {cand_id}')
            print(f'CCD: {ccd}')

            # Plot light curve
            fig, ax = plt.subplots()

            # Grab corresponding appended light curve and forced light curve files for candidate
            unforced_lc_app = glob.glob(f'./lc_files/{field}/{ccd}/cand{cand_id}*')
            unflc_df = pd.read_csv(unforced_lc_app[0])
            print('Unforced light curve file:', unforced_lc_app)

            forced_lc = glob.glob(f'../../web/web/sniff/{field}_tmpl/{ccd}/*/*_cand{cand_id}.forced.*')
            flc_df = pd.read_csv(forced_lc[0], delim_whitespace=True)
            flc_df = flc_df.drop(columns=['tmpl'])

            # Creating i and g band subsets, and removing '-' magnitude values
            unf_i = unflc_df[unflc_df['filt'] == 'i']
            unf_g = unflc_df[unflc_df['filt'] == 'g']
            unf_mi = unf_i[(unf_i['m'] != '-') & (unf_i['dm'] != '-')]
            unf_mg = unf_g[(unf_g['m'] != '-') & (unf_g['dm'] != '-')]

            # Changing markers for good detections
            good_unf_i = unf_mi[unf_mi['good_detection'] == True]
            good_unf_g = unf_mg[unf_mg['good_detection'] == True]

            # Plot unforced photometry data points
            ax.errorbar(unf_mi['dateobs'].astype(float), unf_mi['m'].astype(float), yerr=unf_mi['dm'].astype(float), fmt='None', capsize=2,
            fillstyle='none', linestyle='None', ecolor='r')
            ax.errorbar(unf_mg['dateobs'].astype(float), unf_mg['m'].astype(float), yerr=unf_mg['dm'].astype(float), fmt='None', capsize=2,
            fillstyle='none', linestyle='None', ecolor='b')
            ax.scatter(unf_mi['dateobs'].astype(float), unf_mi['m'].astype(float), c='r', marker='.', label='i band')
            ax.scatter(unf_mg['dateobs'].astype(float), unf_mg['m'].astype(float), c='b', marker='.', label='g band')

            # Mark "good" detections
            ax.scatter(good_unf_i['dateobs'].astype(float), good_unf_i['m'].astype(float), c='r', marker='x')
            ax.scatter(good_unf_g['dateobs'].astype(float), good_unf_g['m'].astype(float), c='b', marker='x')

            if len(flc_df) > 1:
                flc_df.columns = ['MJD', 'dateobs', 'photcode', 'filt', 'flux_c', 'dflux_c', 'type','chisqr', 'ZPTMAG_c', 'm', 'dm', 'ra', 'dec', 'cmpfile', 'tmpl']
                print('Forced light curve file:', forced_lc)

                # Converting date format to match forced lc format: YYMMDD
                det_dates = flc_df['dateobs'].values 
                det_dates = [d.replace('-','')[2:8] for d in flc_df['dateobs'].values]
                flc_df['dateobs'] = det_dates
                flc_df = flc_df.sort_values(by='dateobs')

                # Calculate limiting magnitudes 
                flc_df = limiting_mag(flc_df)
                
                f_i = flc_df[flc_df['filt'] == 'i']
                f_g = flc_df[flc_df['filt'] == 'g']

                f_mi = f_i[(f_i['m'] != '-') & (f_i['dm'] != '-')]
                f_mg = f_g[(f_g['m'] != '-') & (f_g['dm'] != '-')]
                # f_limi = f_i[(f_i['m'] == '-') & (f_i['limiting_mag'] != 0.0)]
                # f_limg = f_g[(f_g['m'] == '-') & (f_g['limiting_mag'] != 0.0)]

                ###### PLOT ALL LIMITING MAGS FOR ALL DAYS #####
                f_limi = f_i[f_i['limiting_mag'] != 0.0]
                f_limg = f_g[f_g['limiting_mag'] != 0.0]
                
                # Removing forced photometry data points on dates where there are unforced photometry data points
                f_mi_cut = f_mi[~np.round(f_mi['MJD'], 5).isin(np.round(unf_mi['MJD'], 5))]
                f_mg_cut = f_mg[~np.round(f_mg['MJD'], 5).isin(np.round(unf_mg['MJD'], 5))]

                # Plot forced photometry data points
                ax.errorbar(f_mi_cut['dateobs'].astype(float), f_mi_cut['m'].astype(float), yerr=f_mi_cut['dm'].astype(float), fmt='None', capsize=2, 
                fillstyle='none', linestyle='None', ecolor='r')
                ax.errorbar(f_mg_cut['dateobs'].astype(float), f_mg_cut['m'].astype(float), yerr=f_mg_cut['dm'].astype(float), fmt='None', capsize=2, 
                fillstyle='none', linestyle='None', ecolor='b')
                ax.scatter(f_mi_cut['dateobs'].astype(float), f_mi_cut['m'].astype(float), edgecolors='r', facecolors='none', marker='o')
                ax.scatter(f_mg_cut['dateobs'].astype(float), f_mg_cut['m'].astype(float), edgecolors='b', facecolors='none', marker='o')

                # Plot limiting magnitude
                ax.scatter(f_limi['dateobs'].astype(float), f_limi['limiting_mag'], c='r', marker='v', alpha=0.2)
                ax.scatter(f_limg['dateobs'].astype(float), f_limg['limiting_mag'], c='b', marker='v', alpha=0.2) 

            else:
                print('Forced light curve file is empty')

                # Plot limiting magnitude using unforced photometry
                unf_limi_ = limiting_mag(unf_mi)
                unf_limg_ = limiting_mag(unf_mi)

                unf_limi = unf_limi_[unf_limi_['limiting_mag'] != 0.0]
                unf_limg = unf_limg_[unf_limg_['limiting_mag'] != 0.0]
                
                # Plot limiting magnitudes
                ax.scatter(unf_limi['dateobs'].astype(float), unf_limi['limiting_mag'], c='r', marker='v', alpha=0.2)
                ax.scatter(unf_limg['dateobs'].astype(float), unf_limg['limiting_mag'], c='b', marker='v', alpha=0.2)

            ax.set_title(f'Candidate {cand_id}')
            ax.set_xlabel('date of observation')
            ax.set_ylabel('mag')
            ax.invert_yaxis()
            fig.autofmt_xdate(rotation=45)
            ax.legend()

            fig_name = f'{field}_ccd{ccd}_cand{cand_id}_unforced.png'

            plt.savefig(f'{lc_outdir}/{fig_name}')

            plt.close()

            print(f'Light curve saved as: {lc_outdir}/{fig_name}')
            print('')

    print(' ')
    print('ALL LIGHT CURVE PLOTS CREATED!')
    print(' ')
