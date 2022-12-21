# Code from Anais Moller

import numpy as np
import pandas as pd
import io
import csv
import logging
import requests

def generate_csv(s, lists):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    _ = [writer.writerow(row) for row in zip(*lists)]

    return s + output.getvalue().replace("\r", "")

def xmatch(id, ra, dec, extcatalog, distmaxarcsec):
    table_header = """ObjectID, ra_in, dec_in\n"""
    table = generate_csv(table_header, [id, ra, dec])

    print('test spot 1')
    print('TABLE')
    print(table)

    r = requests.post("http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync", 
                       data={"request": "xmatch",
                             "distMaxArcsec": distmaxarcsec,
                             "selection": "all",
                             "RESPONSEFORMAT":"csv",
                             "cat2": extcatalog,
                             "colRA1": "ra_in",
                             "colDec1": "dec_in"},
                        files={"cat1": table})

    data = r.content.decode().split("\n")[1:-1]
    header = r.content.decode().split("\n")[0].split(",")

    print('test spot 2')

    # h = open('ps1_text.csv', 'w')
    # h.write(r.text)
    # h.close()

    return data, header

def cross_match_alerts_raw_generic(oid, ra, dec, ctlg, distmaxarcsec):
 
    if len(ra) == 0:
        return []
    try:
        data, header = xmatch(oid, ra, dec, extcatalog=ctlg, distmaxarcsec=distmaxarcsec)
    except (ConnectionError, TimeoutError, ValueError) as ce:
        logging.warning("XMATCH failed " + repr(ce))
        print('test spot 3')
        return []
        
    if len(data) > 0 and "504 Gateway Time-out" in data[0]:
        msg_head = "CDS xmatch service probably down"
        msg_foot = "Check at http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync"
        logging.warning(msg_head)
        logging.warning(data[0])
        logging.warning(msg_foot)
        return []

    data = [x.split(",") for x in data]
    df_search_out = pd.DataFrame(data=np.array(data), columns=header)
    
    if "angDist" not in df_search_out.keys():
        print("Xmatch failure")
        raise Exception
    else:
        df_search_out["angDist"] = df_search_out["angDist"].astype(float)
        if ctlg == "vizier:II/349/ps1":
            df_search_out = df_search_out.rename(columns={"objID": "ObjectID_PS1"})
        df_search_out = df_search_out.rename(columns={"ObjectID": "ObjectID"})
        df_search_out_tmp = df_search_out.sort_values("angDist", ascending=True)
        df_search_out_tmp = df_search_out_tmp.groupby("ObjectID").first()
        df_search_out_tmp = df_search_out_tmp.rename(columns={"ra": "ra_out", "dec": "dec_out"})

        df_out_tmp = pd.DataFrame()
        df_out_tmp["ObjectID"] = oid
        df_out_tmp["ObjectID"] = df_out_tmp["ObjectID"].astype(str)
        df_out_tmp["ra"] = ra
        df_out_tmp["dec"] = dec

        df_out = pd.merge(df_out_tmp, df_search_out_tmp, on="ObjectID", how="left")
        df_out = df_out.fillna("Unknown")
        df_out = df_out.drop(["ra_in", "dec_in"], axis=1)

        return df_out
