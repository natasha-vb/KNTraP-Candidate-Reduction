# Code from Anais Moller

import numpy as np
import pandas as pd
import io
import csv
import logging
import requests

def refine_search_gaia(id, ra, dec, id_out, source, ragaia, decgaia, plx, plxerr, gmag, angDist):
    out = []

    for id_in, ra_in, dec_in, in zip(id, ra, dec,):
        ra_in, dec_in = float(ra_in), float(dec_in)
        id_in = str(id_in)

        if id_in in id_out:
            index = id_out.index(id_in)
            source_tmp = source[index] if source[index] != "" else "Unknown"
            ragaia_tmp = ragaia[index] if ragaia[index] != "" else "Unknown"
            decgaia_tmp = decgaia[index] if decgaia[index] != "" else "Unknown"
            plx_tmp = plx[index] if plx[index] != "" else "Unknown"
            plxerr_tmp = plxerr[index] if plxerr[index] != "" else "Unknown"
            gmag_tmp = gmag[index] if gmag[index] != "" else "Unknown"
            angdist_tmp = angDist[index] if angDist[index] != "" else "Unknown"

            out.append((id_in,
                        ra_in,
                        dec_in,
                        source_tmp,
                        ragaia_tmp,
                        decgaia_tmp,
                        plx_tmp,
                        plxerr_tmp,
                        gmag_tmp,
                        angdist_tmp))

        else:
            out.append((id_in,
                        ra_in,
                        dec_in,
                        "Unknown",
                        "Unknown",
                        "Unknown",
                        "Unknown",
                        "Unknown",
                        "Unknown",
                        "Unknown"))

    return out

def generate_csv(s, lists):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    _ = [writer.writerow(row) for row in zip(*lists)]

    return s + output.getvalue().replace("\r", "")

def xmatch(id, ra, dec, extcatalog, distmaxarcsec):
    table_header = """objectID, ra_in, dec_in\n"""
    table = generate_csv(table_header, [id, ra, dec])

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

    # h = open('gaia_text.csv', 'w')
    # h.write(r.text)
    # h.close()

    return data, header


def cross_match_alerts_raw_gaia(id, ra, dec, ctlg):
    if len(ra) == 0:
        return []

    try:
        data, header = xmatch(id, ra, dec, extcatalog=ctlg, distmaxarcsec=50)
    except (ConnectionError, TimeoutError, ValueError) as ce:
        logging.warning("XMATCH GAIA failed " + repr(ce))
        return []

    if len(data) > 0 and "504 Gateway Time-out" in data[0]:
        msg_head = "CDS xmatch service probably down"
        msg_foot = "Check at http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync"
        logging.warning(msg_head)
        logging.warning(data[0])
        logging.warning(msg_foot)
        return []

    if "DR3Name" not in header:
        print("DR3Name not in gaia header")
        return []

    oid_ind = header.index("objectID")
    dr3name_ind = header.index("DR3Name")
    ragaia_ind = header.index("RAdeg")
    decgaia_ind = header.index("DEdeg")
    parallax_ind = header.index("Plx")
    parallaxerr_ind = header.index("e_Plx")
    gmag_ind = header.index("Gmag")
    angDist_ind = header.index("angDist")

    id_out = [np.array(i.split(","))[oid_ind] for i in data]

    dr3name = [np.array(i.split(","))[dr3name_ind] for i in data]
    ragaia = [np.array(i.split(","))[ragaia_ind] for i in data]
    decgaia = [np.array(i.split(","))[decgaia_ind] for i in data]
    plx = [np.array(i.split(","))[parallax_ind] for i in data]
    plxerr = [np.array(i.split(","))[parallaxerr_ind] for i in data]
    gmag = [np.array(i.split(","))[gmag_ind] for i in data]
    angDist = [np.array(i.split(","))[angDist_ind] for i in data]

    out = refine_search_gaia(id, ra, dec, id_out, dr3name, ragaia, decgaia, plx, plxerr, gmag, angDist)

    return out


def cross_match_gaia(id_list, ra_list, dec_list, ctlg="vizier:I/355/gaiadr3"):

    matches = cross_match_alerts_raw_gaia(id_list, ra_list, dec_list, ctlg)

    xmatch_gaia_source = np.transpose(matches)[3]
    xmatch_gaia_ragaia = np.transpose(matches)[4]
    xmatch_gaia_decgaia = np.transpose(matches)[5]
    xmatch_gaia_plx = np.transpose(matches)[6]
    xmatch_gaia_plxerr = np.transpose(matches)[7]
    xmatch_gaia_gmag = np.transpose(matches)[8]
    xmatch_gaia_angdist = np.transpose(matches)[9]

    return (xmatch_gaia_source,
            xmatch_gaia_ragaia,
            xmatch_gaia_decgaia,
            xmatch_gaia_plx,
            xmatch_gaia_plxerr,
            xmatch_gaia_gmag,
            xmatch_gaia_angdist)