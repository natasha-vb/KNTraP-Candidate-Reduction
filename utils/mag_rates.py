import numpy as np
import pandas as pd

def calculate_mag_diff(lc, verbose=False):

    alpha_temp = pd.DataFrame(columns={'dateobs','filt','mag_diff','date_diff','alpha'})

    # Setting up dataframe for magnitude difference calculations
    alpha_temp['dateobs'] = lc['dateobs']
    alpha_temp['dateobs_int'] = [int(x) for x in alpha_temp['dateobs']]
    alpha_temp['m'] = lc['m'].replace('-', np.NaN)
    alpha_temp['m_flt'] = [float(x) for x in alpha_temp['m']]
    alpha_temp['filt'] = lc['filt']

    # Calculating magnitude difference rates
    alpha_temp['mag_diff'] = alpha_temp['m_flt'].diff()
    alpha_temp['date_diff'] = alpha_temp['dateobs_int'].diff()
    alpha_temp['alpha'] = alpha_temp['mag_diff'].values / alpha_temp['date_diff'].values

    # Deleting columns not needed to merge with light curve file
    alpha_temp.drop('dateobs_int', axis=1, inplace=True)
    alpha_temp.drop('m', axis=1, inplace=True)
    alpha_temp.drop('m_flt', axis=1, inplace=True)
    alpha_temp.drop('mag_diff', axis=1, inplace=True)
    alpha_temp.drop('date_diff', axis=1, inplace=True)

    if verbose:
        print(alpha_temp)

    return alpha_temp

def mag_rates(lc_file, verbose=False):

    lc_file_i = lc_file[lc_file['filt'] == 'i']
    lc_file_g = lc_file[lc_file['filt'] == 'g']

    if verbose:
        print(' ')
        print('----------------------------------')
        print('MAGNITUDE CHANGE RATE CALCULATIONS')

    if len(lc_file_i) != 0:
        alpha_i = calculate_mag_diff(lc_file_i, verbose=True)
    else:
        alpha_i = pd.DataFrame(columns={'dateobs','filt','alpha'})
    
    if len(lc_file_g) != 0:
        alpha_g = calculate_mag_diff(lc_file_g, verbose=True)
    else:
        alpha_g = pd.DataFrame(columns={'dateobs','filt','alpha'})

    alpha = pd.merge(alpha_i, alpha_g, how='outer', on=['dateobs','filt'], suffixes=('_i','_g'))

    if verbose:
        print('Alpha values:')
        print(alpha)
        print('----------------------------------')
        print(' ')

    return alpha