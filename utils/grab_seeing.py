import glob
import pandas as pd

def grab_seeing(lcfile, field, ccd):

    for d in lcfile['dateobs']:
        date = (d + 20000000) - 1 
        obslog = glob.glob(f'./observinglogs/{date}.qcinv')
        if date == 20220221:
            df_obslog = pd.read_csv(obslog,header=None, skiprows=[0,1,2,3], delim_whitespace=True)
        
        else:
            df_obslog = pd.read_csv(obslog,header=None, skiprows=[0,1,2], delim_whitespace=True)
        
        df_obslog.columns = ['#expid', 'ra', 'dec', 'ut', 'fil', 'time', 'secz', 'psf', 'sky', 'cloud', 'teff', 'Object']

        df_obslog_field = df_obslog[df_obslog['Object'] = field]

        
