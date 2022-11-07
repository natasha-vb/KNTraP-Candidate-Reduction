import glob 
import matplotlib.pyplot as plt
import os
import pandas as pd


if __name__ == "__main__":

    # Grab all masterlists of filtered candidates 
    filtered_mlists = glob.glob(f'./masterlist/*/priority/*.csv')

    for f in filtered_mlists:
        
        # Setting up directory to save light curves. Directory name is the filtering criteria parameters
        field = f.split('_')[-1].split('.')[0]
        lc_dir_name = f.split('/')[-1].replace('.csv','')

        lc_outdir = (f'./lc_files/{field}/filtered_candidates/{lc_dir_name}')
        if not os.path.exists(lc_outdir):
            os.makedirs(lc_outdir)
        
        # Read in masterlist
        df = pd.read_csv(f, sep=',', comment='#', header=11, skipinitialspace=True)

        # Iterate over candidates within masterlist 
        for i in len(df):
            cand = df.iloc[i]

            cand_id = cand['CAND_ID']
            ccd = cand['CCD']

            # Grab corresponding appended light curve and forced light curve files for candidate
            unforced_lc_app = glob.glob(f'./lc_files/{field}/{ccd}/cand{cand_id}*')
            unflc_df = pd.read_csv('unforced_lc_app')

            forced_lc = glob.glob(f'../../web/web/sniff/{field}_tmpl/{ccd}/*/*_cand{cand_id}.forced.*')
            flc_df = pd.read_csv('forced_lc')

            det_dates = flc_df['dateobs'].values 
            det_dates = [f'{d.replace('-','')[2:8]}' for d in flc_df['dateobs'].values]
            flc_df['dateobs'] = det_dates
            flc_df = flc_df.sort_values(by="dateobs")

            # Plot light curve
            unf_i = unflc_df[unflc_df['filt'] == 'i']
            unf_g = unflc_df[unflc_df['filt'] == 'g']

            f_i = flc_df[flc_df['filt'] == 'i']
            f_g = flc_df[flc_df['filt'] == 'g']

            plt.scatter(unf_i['dateobs'], unf_i['m'], c='r')
            plt.scatter(unf_g['dateobs'], unf_i['m'], c='b')

            plt.scatter(f_i['dateobs'], f_i['m'], edgecolors='r', facecolors=None)
            plt.scatter(f_g['dateobs'], f_i['m'], edgecolors='b', facecolors=None)

            fig_name = f'cand{cand_id}_{field}_ccd{ccd}.png'

            plt.savefig(f'{lc_outdir}/{fig_name}')




