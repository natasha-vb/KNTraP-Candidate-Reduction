import pandas as pd 
import numpy as np

def consecutive_count(lcfile, verbose=False):
    
    # Constructing dataframe of all nights 
    df = pd.DataFrame({'dateobs':[220212,220213,220214,220215,220216,220217,220218,220219,220220,220221,220222]})
    
    # Putting relevant columns from light curve file into temp dataframe
    lc = pd.DataFrame()
    lc['dateobs'] = lcfile['dateobs']
    lc['filt'] = lcfile['filt']
    lc['good'] = lcfile['good_detection']

    # Merging light curve data into all nights dataframe 
    dfmerge = pd.merge(df, lc, how='outer', on=['dateobs'])

    dfmerge['detection_i'] = dfmerge.apply(lambda row: True if row['filt'] == 'i' else False, axis=1)
    dfmerge['good_i'] = dfmerge.apply(lambda row: True if row['filt'] == 'i' and row['good'] == True else False, axis=1)

    dfmerge['detection_g'] = dfmerge.apply(lambda row: True if row['filt'] == 'g' else False, axis=1)
    dfmerge['good_g'] = dfmerge.apply(lambda row: True if row['filt'] == 'g' and row['good'] == True else False, axis=1)

    del dfmerge['filt'], dfmerge['good']

    dfm = dfmerge.groupby(['date']).sum()

    if verbose:
        print('Detections over all nights')
        print(dfm)
    
    ##### count consecutive 
    #### return dataframe with all consecutive counts