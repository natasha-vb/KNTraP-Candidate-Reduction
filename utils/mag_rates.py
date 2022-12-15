import pandas as pd

def calculate_mag_diff(lc, verbose=False):

    alpha_temp = pd.DataFrame()

    for i in range(len(lc)):
        lc_row = lc.iloc[i]
        date_2 = lc_row['dateobs']
        filter = lc_row['filt']
        mag_2 = lc_row['m']

        # Calculate change in mag from previous detection, alpha (mag/night)
        if i == 0:
            alpha = 'NaN'
        else:
            lc_prev_row = lc.iloc[i-1]
            date_1 = lc_prev_row['dateobs']
            mag_1 = lc_prev_row['m']

            alpha = (float(mag_2) - float(mag_1)) / (int(date_2) - int(date_1))

            if verbose:
                print(f'{filter} mag diff calculation:')
                print(f'{mag_2} - {mag_1} / {date_2} - {date_1} = {alpha}')
        
        alpha_temp = alpha_temp.append([{'dateobs': date_2,
                                         'filt':filter,
                                         'alpha':alpha}])
    return alpha_temp

def mag_rates(lc_file, verbose=False):

    lc_file_i = lc_file[lc_file['filt'] == 'i']
    lc_file_g = lc_file[lc_file['filt'] == 'g']

    if len(lc_file_i) != 0:
        alpha_i = calculate_mag_diff(lc_file_i, verbose=True)
    else:
        alpha_i = pd.DataFrame(columns={'dateobs','filt','alpha'})
    
    if len(lc_file_g) != 0:
        alpha_g = calculate_mag_diff(lc_file_g, verbose=True)
    else:
        alpha_g = pd.DataFrame(columns={'dateobs','filt','alpha'})

    if verbose:
        print('Alpha i band values:')
        print(alpha_i)
        print('Alpha g band values:')
        print(alpha_g)

    alpha = pd.merge(alpha_i, alpha_g, how='left', on=['dateobs','filt'], suffixes=('_i','_g'))

    if verbose:
        print('Alpha values:')
        print(alpha)

    return alpha