# Code from Anais Moller

import numpy as np
import pandas as pd
import io
import csv
import logging
import requests

def refine_search(id, ra, dec, names, types, id_out, redshifts, sp_types):
    out = []

    for id_in, ra_in, dec_in in zip(id, ra, dec):
        ra_in, dec_in = float(ra_in), float(dec_in)
        id_in = str(id_in)

        if id_in in id_out:
            index = id_out.index(id_in)
            sp_type_tmp = sp_types[index] if sp_types[index] != "" else "Unknown"
            redshift_tmp = redshifts[index] if redshifts[index] != "" else "Unknown"
            out.append((id_in, ra_in, dec_in, 
                         str(names[index]),
                         str(types[index]),
                         str(redshift_tmp),
                         str(sp_type_tmp)
                         ))
        else:
            out.append((id_in, ra_in, dec_in, "Unknown", "Unknown", "Unknown", "Unknown"))

    return out

def generate_csv(s, lists):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    _ = [writer.writerow(row) for row in zip(*lists)]

    return s + output.getvalue().replace("\r", "")


def xmatch(id, ra, dec, distmaxarcsec):
    table_header = """objectID, ra_in, dec_in\n"""
    table = generate_csv(table_header, [id, ra, dec])

    #### TESTING
    print('XMATCH TABLE:')
    print(table)
    
    cnt = 1
    tablesplit = table.split('\n')
    tablecut = tablesplit[1:-1]
    for i in len(tablecut):
        row = tablecut[i]
        print('Count =', cnt)
        print('TABLE ROW:')
        print(row)
        r = requests.post("http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync", 
                        data={"request": "xmatch",
                                "distMaxArcsec": distmaxarcsec,
                                "selection": "all",
                                "RESPONSEFORMAT":"csv",
                                "cat2": "simbad",
                                "colRA1": "ra_in",
                                "colDec1": "dec_in"},
                            files={"cat1": row})

        data = r.content.decode().split("\n")[1:-1]
        header = r.content.decode().split("\n")[0].split(",")

        cnt +=1
            
    # h = open('simbad_text.csv', 'w')
    # h.write(r.text)
    # h.close()

    return data, header

def crossmatch_alerts_simbad(id_list, ra_list, dec_list):
    if len(ra_list) == 0:
        return []
    
    try:
        data, header = xmatch(id_list, ra_list, dec_list, distmaxarcsec=50)
    except (ConnectionError, TimeoutError, ValueError) as ce:
        logging.warning("XMATCH failed " + repr(ce))
        return []
    
    if len(data) > 0 and "504 Gateway Time-out" in data[0]:
        msg_head = "CDS xmatch service probably down"
        msg_foot = "Check at http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync"
        logging.warning(msg_head)
        logging.warning(data[0])
        logging.warning(msg_foot)
        return []
    
    if "main_id" not in header:
        print("main_id not in header")
        return []
    
    main_id = header.index("main_id")
    main_type = header.index("main_type")
    id_ind = header.index("objectID")
    redshift_ind = header.index("redshift")
    sp_type_ind = header.index("sp_type")

    names = [np.array(i.split(","))[main_id] for i in data]
    types = [np.array(i.split(","))[main_type] for i in data]
    id_out = [np.array(i.split(","))[id_ind] for i in data]    
    redshifts = [np.array(i.split(","))[redshift_ind] for i in data]
    sp_types = [np.array(i.split(","))[sp_type_ind] for i in data]
    
    out = refine_search(id_list, ra_list, dec_list, names, types, id_out, redshifts, sp_types)

    return out

def crossmatch_simbad(id_list, ra_list, dec_list):
    matches = crossmatch_alerts_simbad(id_list, ra_list, dec_list)
    xmatch_redshift = np.transpose(matches)[-1]
    xmatch_sptype = np.transpose(matches)[-2]
    xmatch_type = np.transpose(matches)[-3]
    xmatch_ctlg = np.transpose(matches)[-4]

    return (xmatch_redshift, xmatch_sptype, xmatch_type, xmatch_ctlg)