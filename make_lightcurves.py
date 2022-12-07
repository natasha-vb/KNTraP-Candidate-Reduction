import argparse
import glob 
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import ipdb 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Source Extractor to filter transient candidates")
    parser.add_argument(
            "--field",
            type=str,
            help="Selected field"
    )
    args = parser.parse_args()

    matplotlib.use('Agg') 

    # Grab all masterlists of filtered candidates 
    if args.field:
        filtered_mlists = glob.glob(f'./masterlist/{args.field}/priority/*.csv')
    else:
        filtered_mlists = glob.glob(f'./masterlist/*/priority/*.csv')

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

            # Grab corresponding appended light curve and forced light curve files for candidate
            unforced_lc_app = glob.glob(f'./lc_files/{field}/{ccd}/cand{cand_id}*')
            unflc_df = pd.read_csv(unforced_lc_app[0])
            print('Unforced light curve file:', unforced_lc_app)

            forced_lc = glob.glob(f'../../web/web/sniff/{field}_tmpl/{ccd}/*/*_cand{cand_id}.forced.*')
            flc_df = pd.read_csv(forced_lc[0], delim_whitespace=True)
            flc_df = flc_df.drop(columns=['tmpl'])
            flc_df.columns = ['MJD', 'dateobs', 'photcode', 'filt', 'flux_c', 'dflux_c', 'type','chisqr', 'ZPTMAG_c', 'm', 'dm', 'ra', 'dec', 'cmpfile', 'tmpl']
            print('Forced light curve file:', forced_lc)

            # Converting date format to match forced lc format: YYMMDD
            det_dates = flc_df['dateobs'].values 
            det_dates = [d.replace('-','')[2:8] for d in flc_df['dateobs'].values]
            flc_df['dateobs'] = det_dates
            flc_df = flc_df.sort_values(by='dateobs')

            # Calculate limiting magnitudes
            flc_df['limiting_mag'] = 0.0
            for ii, row in flc_df.iterrows():
                if row['flux_c'] >= 0:
                    flc_df['limiting_mag'][ii] = -2.5*(np.log10(row['flux_c'] + 3*(row['dflux_c']))) + row['ZPTMAG_c']
                else:
                    flc_df['limiting_mag'][ii] = -2.5*(np.log10(3*(row['dflux_c']))) + row['ZPTMAG_c']

            # Creating i and g band subsets, and removing '-' magnitude values
            unf_i = unflc_df[unflc_df['filt'] == 'i']
            unf_g = unflc_df[unflc_df['filt'] == 'g']
            unf_mi = unf_i[unf_i['m'] != '-']
            unf_mg = unf_g[unf_g['m'] != '-']

            f_i = flc_df[flc_df['filt'] == 'i']
            f_g = flc_df[flc_df['filt'] == 'g']

            f_mi = f_i[f_i['m'] != '-']
            f_mg = f_g[f_g['m'] != '-']
            f_limi = f_i[f_i['m'] == '-']
            f_limg = f_g[f_g['m'] == '-']

            f_mi_cut = f_mi[~np.round(f_mi['MJD'], 5).isin(np.round(unf_mi['MJD'], 5))]
            f_mg_cut = f_mg[~np.round(f_mg['MJD'], 5).isin(np.round(unf_mg['MJD'], 5))]

            # Changing markers for good detections
            good_unf_i = unf_mi[unf_mi['good_detection'] == True]
            good_unf_g = unf_mg[unf_mg['good_detection'] == True]

            # Plot unforced light curve
            fig, ax = plt.subplots()

            # ax.scatter(f_mi_cut['dateobs'].astype(float), f_mi_cut['m'].astype(float), c='r', marker='.')
            ax.scatter(f_limi['dateobs'].astype(float), f_limi['limiting_mag'],    c='r', marker='v', alpha=0.2)
            # ax.scatter(f_mg_cut['dateobs'].astype(float), f_mg_cut['m'].astype(float), c='b', marker='.')
            ax.scatter(f_limg['dateobs'].astype(float), f_limg['limiting_mag'],    c='b', marker='v', alpha=0.2) 

            ax.scatter(unf_mi['dateobs'].astype(float), unf_mi['m'].astype(float), c='r', marker='.', label='i band')
            ax.scatter(unf_mg['dateobs'].astype(float), unf_mg['m'].astype(float), c='b', marker='.', label='g band')

            ax.scatter(good_unf_i['dateobs'].astype(float), good_unf_i['m'].astype(float), c='r', marker='x')
            ax.scatter(good_unf_g['dateobs'].astype(float), good_unf_g['m'].astype(float), c='b', marker='x')
            
            ax.set_title(f'Candidate {cand_id}')
            ax.set_xlabel('date of observation')
            ax.set_ylabel('mag')
            ax.invert_yaxis()
            fig.autofmt_xdate(rotation=45)
            ax.legend()

            fig_name = f'{field}_ccd{ccd}_cand{cand_id}_unforced.png'

            plt.savefig(f'{lc_outdir}/{fig_name}')

            print(f'Light curve saved as: {lc_outdir}/{fig_name}')
            print('')

            # Plot light curve with forced photometry points
            fig, ax = plt.subplots()

            ax.scatter(f_mi_cut['dateobs'].astype(float), f_mi_cut['m'].astype(float), edgecolors='r', facecolor=None, marker='o')
            ax.scatter(f_limi['dateobs'].astype(float), f_limi['limiting_mag'], c='r', marker='v', alpha=0.2)
            ax.scatter(f_mg_cut['dateobs'].astype(float), f_mg_cut['m'].astype(float), edgecolors='b', facecolor=None, marker='o')
            ax.scatter(f_limg['dateobs'].astype(float), f_limg['limiting_mag'], c='b', marker='v', alpha=0.2) 

            ax.scatter(unf_mi['dateobs'].astype(float), unf_mi['m'].astype(float), c='r', marker='.', label='i band')
            ax.scatter(unf_mg['dateobs'].astype(float), unf_mg['m'].astype(float), c='b', marker='.', label='g band')

            ax.scatter(good_unf_i['dateobs'].astype(float), good_unf_i['m'].astype(float), c='r', marker='x')
            ax.scatter(good_unf_g['dateobs'].astype(float), good_unf_g['m'].astype(float), c='b', marker='x')
            
            ax.set_title(f'Candidate {cand_id}')
            ax.set_xlabel('date of observation')
            ax.set_ylabel('mag')
            ax.invert_yaxis()
            fig.autofmt_xdate(rotation=45)
            ax.legend()

            fig_name = f'{field}_ccd{ccd}_cand{cand_id}_forced.png'

            plt.savefig(f'{lc_outdir}/{fig_name}')

            print(f'Light curve saved as: {lc_outdir}/{fig_name}')
            print('')

    print('All light curve plots created!')