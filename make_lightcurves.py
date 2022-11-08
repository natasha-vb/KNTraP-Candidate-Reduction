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
            print('Unforced light curve file:', unforced_lc_app)
            unflc_df = pd.read_csv(unforced_lc_app[0])

            forced_lc = glob.glob(f'../../web/web/sniff/{field}_tmpl/{ccd}/*/*_cand{cand_id}.forced.*')
            print('Forced light curve file:', forced_lc)
            flc_df = pd.read_csv(forced_lc[0])
            print('FORCED LIGHT CURVE FILE:', flc_df)
            print(flc_df)

            det_dates = flc_df['dateobs'].values 
            det_dates = [d.replace('-','')[2:8] for d in flc_df['dateobs'].values]
            flc_df['dateobs'] = det_dates
            flc_df = flc_df.sort_values(by="dateobs")

            # Plot light curve
            unf_i = unflc_df[unflc_df['filt'] == 'i']
            unf_g = unflc_df[unflc_df['filt'] == 'g']

            f_i = flc_df[flc_df['filt'] == 'i']
            f_g = flc_df[flc_df['filt'] == 'g']

            # Changing markers for good detections
            good_unf_i = unf_i['good_detection']
            good_unf_g = unf_g['good_detection']
            good_f_i = f_i['good_detection']
            good_f_g = f_g['good_detection']

            m_unf_i = ['X' if val==True else '.' for val in good_unf_i]
            m_unf_g = ['X' if val==True else '.' for val in good_unf_g]
            m_f_i = ['X' if val==True else '.' for val in good_f_i]
            m_f_g = ['X' if val==True else '.' for val in good_f_g]

            fig, ax = plt.subplots()

            for x, y, m in zip(unf_i['dateobs'], unf_i['m'], m_unf_i, label = 'i band'):
                ax.scatter(x, y, c='r', marker=m)
            for x, y, m in zip(unf_g['dateobs'], unf_g['m'], m_unf_g, label = 'g band'):
                ax.scatter(x, y, c='b', marker=m)

            for x, y, m in zip(f_i['dateobs'], f_i['m'], m_f_i):
                ax.scatter(x, y, edgecolors='r', facecolors=None, marker=m)
            for x, y, m in zip(f_g['dateobs'], f_g['m'], m_f_g):
                ax.scatter(x, y, edgecolors='b', facecolors=None, marker=m)
            
            ax.set_title(f'Candidate {cand_id}')
            ax.set_xlabel('date of observation')
            ax.set_ylabel('mag')
            ax.invert_yaxis()
            ax.legend()

            fig_name = f'cand{cand_id}_{field}_ccd{ccd}.png'

            plt.savefig(f'{lc_outdir}/{fig_name}')




