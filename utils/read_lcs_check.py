import pandas as pd
import glob
from astropy.table import Table

def read_clusterfile(filename):
    """Read cluster file from PHOTPIPE

    Args:
        filename (str): Filename to read
    Return:
        df (pd.DataFrame): Dataframe with id,ra,dec in cluster file
    """
    # Count lines to split cluster file in tables
    counter = 0
    list_counter_ht = []
    len_file = 0
    with open(filename) as file:
        for line in file:
            if "#" in line:
                list_counter_ht.append(counter)
            counter += 1
            len_file += 1

    df = pd.read_csv(
        filename,
        skiprows=list_counter_ht[1],
        skipfooter=len_file - list_counter_ht[2],
        delimiter=r"\s+",
        engine="python",
    )

    df.columns = df.columns[1:].tolist() + ["dummy"]

    return df[["ID", "RAaverage", "DECaverage"]]

def read_file(fname):
    try:
        df_tmp = Table.read(fname, format="ascii").to_pandas()
        df = pd.read_table(fname, header=None, skiprows=1, delim_whitespace=True)
        df.columns = [
                    "MJD",
                    "dateobs",
                    "photcode",
                    "filt",
                    "flux_c",
                    "dflux_c",
                    "type",
                    "chisqr",
                    "ZPTMAG_c",
                    "m",
                    "dm",
                    "ra",
                    "dec",
                    "cmpfile",
                    "tmpl",
                ]
        df_tmp = df.copy()

        return df_tmp

    except Exception:
        print("File corrupted or empty", fname)
        df_tmp = pd.DataFrame()
        return df_tmp

def get_lcs_ids(filename):
    """Get light curve file candidate IDs

    Args:
        filename (str): Filename to read
    Return:
        ID (str): Candidate ID
    """
    id = filename.split('.')[-4].split('cand')[1]

    return id


# Which CCD and field to test
field = '257C'

count = 0
for i in range (1,63,1):
    print('============================================================')
    ccd   = i
    print('ccd', ccd)

    # Read in cluster file
    try:
        cluster = glob.glob(f'/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/web/web/sniff/{field}_tmpl/{ccd}/*.clusters')
        cluster_info = read_clusterfile(cluster[0])
    except:
        print('Cluster file not found')
        continue

    ids = cluster_info['ID']

    # Grab all light curves
    lcs = glob.glob(f'/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/web/web/sniff/{field}_tmpl/{ccd}/*/*unforced.difflc.txt')
    list_lcs_ids = []
    for lc in lcs:
        id = get_lcs_ids(lc)
        list_lcs_ids.append(id)

    # Crossmatch lc ids against clusters file list
    list_lcs_ids_int = [int(x) for x in list_lcs_ids]
    no_xmatch = [x for x in cluster_info['ID'] if x not in list_lcs_ids_int]

    print('Candidates with no clusters match in light curves')
    print(no_xmatch)
    print(' ')

    # Try to read in light curves
    
    for lc in lcs:
        df = read_file(lc)

        if len(df) > 1:
            # print(lc, 'read ok :)')
            continue
        else:
            # print(lc, 'NOT READ OK :(')
            count += 1

print('Number of empty light curves:', count)