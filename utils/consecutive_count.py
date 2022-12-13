import pandas as pd 
import numpy as np

def consecutive_count(lcfile, verbose=False):
    
    # Constructing dataframe of all nights 
    df = pd.DataFrame({'dateobs':[220212,220213,220214,220215,220216,220217,220218,220219,220220,220221,220222]})
    
    # Putting relevant columns from light curve file into temp dataframe
    lc = pd.DataFrame()
    lc['dateobs'] = lcfile['dateobs'].astype(int)
    lc['filt'] = lcfile['filt']
    lc['good'] = lcfile['good_detection']

    # Merging light curve data into all nights dataframe 
    dfmerge = pd.merge(df, lc, how='outer', on=['dateobs'])

    dfmerge['detection_i'] = dfmerge.apply(lambda row: True if row['filt'] == 'i' else False, axis=1)
    dfmerge['good_i'] = dfmerge.apply(lambda row: True if row['filt'] == 'i' and row['good'] == True else False, axis=1)

    dfmerge['detection_g'] = dfmerge.apply(lambda row: True if row['filt'] == 'g' else False, axis=1)
    dfmerge['good_g'] = dfmerge.apply(lambda row: True if row['filt'] == 'g' and row['good'] == True else False, axis=1)

    del dfmerge['filt'], dfmerge['good']

    dfm = dfmerge.groupby(['dateobs']).sum()
    dfm['detection_i'] = dfm['detection_i'].astype(int)
    dfm['good_i'] = dfm['good_i'].astype(int)
    dfm['detection_g'] = dfm['detection_g'].astype(int)
    dfm['good_g'] = dfm['good_g'].astype(int)

    if verbose:
        print('Detections over all nights')
        print(dfm)
    
    # Counting consecutive i band detections 
    ibanddet = dfm['detection_i']
    ibandgood = dfm['good_i']
    ibandboth = ibanddet & ibandgood
    icount = ''.join(ibandboth.astype('str').tolist()).split('0')
    icountsum = [int(np.sum([int(digit) for digit in num])) for num in icount]
    
    if verbose:
        print('Max number of consecutive i band detections:',max(icountsum))
    
    # Counting consecutive i band detections with one hole
    icountsum2 = []
    if len(icountsum) > 1:
        for i,num in enumerate(icountsum[:-1]):
            x = icountsum[i] + icountsum[i+1]
            icountsum2.append(x)
        if verbose:
            print('Max number of consecutive i band detections w/ one hole:', max(icountsum2))
    else:
        icountsum2 = icountsum
        if verbose:
            print('Max number of consecutive i band detections w/ one hole:', max(icountsum2))

    # Counting consecutive g band detections
    gbanddet = dfm['detection_g']
    gbandgood = dfm['good_g']
    gbandboth = gbanddet & gbandgood
    gcount = ''.join(gbandboth.astype('str').tolist()).split('0')
    gcountsum = [int(np.sum([int(digit) for digit in num])) for num in gcount]

    if verbose:
        print('Max number of consecutive g band detections:', max(gcountsum))

    # Counting consecutive g band detections with one hole
    gcountsum2 = []
    if len(gcountsum) > 1:
        for i,num in enumerate(gcountsum[:-1]):
            x = gcountsum[i] + gcountsum[i+1]
            gcountsum2.append(x)
        if verbose:
            print('Max number of consecutive g band detections w/ one hole:', max(gcountsum2))
    else:
        gcountsum2 = gcountsum
        if verbose:
            print('Max number of consecutive g band detections w/ one hole:', max(gcountsum2))

    # Counting consecutive detections in both i and g bands
    igbandboth = (ibanddet & ibandgood) & (gbanddet & gbandgood)
    igcount = ''.join(igbandboth.astype('str').tolist()).split('0')
    igcountsum = [int(np.sum([int(digit) for digit in num])) for num in igcount]

    if verbose:
        print('Max number of consecutive g band detections:', max(igcountsum))

    # Counting consecutive detections in both i and g bands with one hole
    igcountsum2 = []
    if len(igcountsum)>1:
        for i,num in enumerate(igcountsum[:-1]):
            x = igcountsum[i] + igcountsum[i+1]
            igcountsum2.append(x)
        if verbose:
            print('Max number of consecutive i & g band detections w/ one hole:', max(igcountsum2))
    else:
        igcountsum2 = igcountsum
        if verbose:
            print('Max number of consecutive i & g band detections w/ one hole:', max(igcountsum2))

    # Counting consecutive detections in both i and g bands with two holes
    igcountsum3 = []
    if len(igcountsum)>2:
        for i,num in enumerate(igcountsum[:-2]):
            x = igcountsum[i] + igcountsum[i+1] + igcountsum[i+2]
            igcountsum3.append(x)
        if verbose:
            print('Max number of consecutive i & g band detections w/ two holes:', max(igcountsum3))

    elif len(igcountsum)>1:
        igcountsum3 = igcountsum2
        if verbose:
            print('Max number of consecutive i & g band detections w/ two holes:', max(igcountsum3))

    else:
        igcountsum3 = igcountsum
        if verbose:
            print('Max number of consecutive i & g band detections w/ two holes:', max(igcountsum3))

    conseq = pd.DataFrame({'i':     [max(icountsum)],
                           'i_1h':  [max(icountsum2)],
                           'g':     [max(gcountsum)],
                           'g_1h':  [max(gcountsum2)],
                           'ig':    [max(igcountsum)],
                           'ig_1h': [max(igcountsum2)],
                           'ig_2h': [max(igcountsum3)]
                           })

    return conseq