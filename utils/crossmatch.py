from utils.misc import xmatchsimbad
from utils.misc import xmatchgaia
from utils.misc import xmatchps1

def crossmatch(candfile, verbose=False):

    # SIMBAD crossmatch
    print('Crossmatching with Simbad...')
    z, sptype, typ, ctlg = xmatchsimbad.crossmatch_simbad(candfile["CAND_ID"].to_list(),
                                                          candfile["RA_AVERAGE"].to_list(),
                                                          candfile["DEC_AVERAGE"].to_list())

    candfile["simbad_type"] = typ
    candfile["simbad_ctlg"] = ctlg
    candfile["simbad_sptype"] = sptype
    candfile["simbad_redshift"] = z 

    # GAIA Crossmatch
    print('Crossmatching with Gaia...')
    (source_dr3, ragaia_dr3, decgaia_dr3, plx_dr3, plxerr_dr3, gmag_dr3, angdist_dr3) = xmatchgaia.cross_match_gaia( 
                                                                                        candfile["CAND_ID"].to_list(),
                                                                                        candfile["RA_AVERAGE"].to_list(),
                                                                                        candfile["DEC_AVERAGE"].to_list(),
                                                                                        ctlg="vizier:I/355/gaiadr3")
    
    candfile["gaia_DR3_parallax"] = plx_dr3
    candfile["gaia_DR3_parallaxerr"] = plxerr_dr3
    candfile["gaia_sigma"] = (candfile["gaia_DR3_parallax"][candfile["gaia_DR3_parallax"] != "Unknown"].astype(float) / 
                              candfile["gaia_DR3_parallaxerr"][candfile["gaia_DR3_parallaxerr"] != "Unknown"].astype(float))
    
    # Pan-STARRS 1 crossmatch
    ##### NEED TO FIX THIS ###
    print('Crossmatching with Pan-STARRS...')
    df_ps1 = xmatchps1.cross_match_alerts_raw_generic(candfile["CAND_ID"].to_list(),
                                                      candfile["RA_AVERAGE"].to_list(),
                                                      candfile["DEC_AVERAGE"].to_list(),
                                                      ctlg="vizier:II/349/ps1",
                                                      distmaxarcsec=2)
    candfile["ps1_objID"] = df_ps1["ObjectID_PS1"]
    candfile["ps1_objID"] = df_ps1["angDist"]
    
    if verbose:
        print('')
        print('===================')
        print('CROSSMATCH RESULTS:')
        print('===================')
        print('SIMBAD:')
        print('----------------------------------------------------------------------')
        print(candfile[["CAND_ID","simbad_type","simbad_ctlg","simbad_sptype","simbad_redshift"]])
        print('')
        print('GAIA:')
        print('---------------------------------------------------------------')
        print(candfile[["CAND_ID","gaia_DR3_parallax","gaia_DR3_parallaxerr","gaia_sigma"]])
        print('')
        print('PAN_STARRS 1:')
        print('--------------------------------')
        print(candfile[["CAND_ID","ps1_objID","ps1_objID"]])

    return candfile