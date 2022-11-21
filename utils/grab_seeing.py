import glob
import pandas as pd

def grab_seeing(lcfile, field, ccd):

    df_seeing = pd.DataFrame()
    
    if field == 'SCVZ':
        field = 'S-CVZ'
    elif field == 'KNTRAPaa':
        field = 'KNTRAP1'
    elif field == 'FOURHR':
        field == '4hr'

    for i in range(len(lcfile)):
        lc_row = lcfile.iloc[i]
        date = lc_row['dateobs']
        filter = lc_row['filt']

        # Adjusting date to match format in qcinv filenames (YYYYMMDD)
        date_int = int(date)
        date_adj = (date_int + 20000000) - 1 
        obslog = glob.glob(f'./observinglogs/{date_adj}.qcinv')

        # Skip the empty rows at top of the DataFrame
        if date_adj == 20220221:
            df_obslog = pd.read_csv(obslog[0],header=None, skiprows=[0,1,2,3], delim_whitespace=True)
        else:
            df_obslog = pd.read_csv(obslog[0],header=None, skiprows=[0,1,2], delim_whitespace=True)
        
        df_obslog.columns = ['#expid', 'ra', 'dec', 'ut', 'filt', 'time', 'secz', 'psf', 'sky', 'cloud', 'teff', 'Object']

        df_obslog_field = df_obslog[df_obslog['Object'] == field]
        df_obslog_seeing = df_obslog_field['psf'][df_obslog_field['filt'] == filter]

        if len(df_obslog_seeing) > 1:
            # sum up all the seeing values and average them
            df_obslog_sum = sum(df_obslog_seeing)
            df_obslog_ave = df_obslog_sum/len(df_obslog_sum)
            seeing = df_obslog_ave
        else:
            seeing = df_obslog_seeing.iloc[0]
        
        df_seeing = df_seeing.append([{'dateobs': date, 
                                       'filt': filter,
                                       'seeing': float(seeing)}])

    return df_seeing

        
