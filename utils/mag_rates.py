import pandas as pd

def calculate_mag_diff(lc):

    alpha_temp = pd.DataFrame()

    for i in range(len(lc)):
        lc_row = lc.iloc[i]
        date = lc_row['dateobs']
        filter = lc_row['filt']
        mag_2 = lc_row['m']

        # Calculate change in mag from previous night, alpha
        if i == 1:
            alpha = 'NaN'
        else:
            lc_prev_row = lc.iloc[i-1]
            mag_1 = lc_prev_row['m']
            alpha = mag_2 - mag_1
        
        alpha_temp = alpha_temp.append([{'dateobs': date,
                                         'filt':filter,
                                         'alpha':alpha}])
    return alpha_temp

def mag_rates(lc_file):

    lc_file_i = lc_file[lc_file['filt'] == 'i']
    lc_file_g = lc_file[lc_file['filt'] == 'g']

    alpha_i = calculate_mag_diff(lc_file_i)
    alpha_g = calculate_mag_diff(lc_file_g)

    alpha = pd.merge(alpha_i, alpha_g, how='left', on=['dateobs','filt'])

    return alpha