import pandas as pd
import numpy as np
import glob
import re 

import astropy.io.ascii as ascii
from astropy.coordinates import SkyCoord
from astropy import units as u

def cat_match(datemjd, date, ra, dec, filt, field='257A', ccd='1', verbose=False):
        # For deep fields use datemjd, for shallow fields use date
        match_list = glob.glob(f'./cats/{field}/{ccd}/*.{filt}.{date}.*.cat')
        df_cattmp = pd.DataFrame()

        df_cattmp["dateobs"] = [f"{date}"]
        df_cattmp["filt"]    = [f"{filt}"]

        for m in match_list:
            cat = ascii.read(m)
            df_cat = pd.DataFrame(cat.as_array())

            ps = re.compile("sci")
            m_sci = ps.search(m)
            pt = re.compile("tmpl")
            m_tmpl = pt.search(m)
            if m_sci:
                column_ending = "SCI"
            elif m_tmpl:
                column_ending = "TMPL"
            else:
                column_ending = "DIFF"

            # Matching detection coordinates to SE catalogue
            coords_det = SkyCoord(ra=[ra], dec=[dec],unit='deg')
            coords_cat = SkyCoord(ra=df_cat["X_WORLD"], dec=df_cat["Y_WORLD"],unit='deg')

            idx, d2d, d3d = coords_det.match_to_catalog_3d(coords_cat)

            # Separation constraint (~ 1 arcsec) ### might not match with only 1 arcsec, try 2 arcsecs
            sep_constraint = d2d < (2 * u.arcsec)

            df_cat_matched = df_cat.iloc[idx[sep_constraint]]

            if df_cat_matched.empty:
                # Replace empty catalog match dataframe values with NaNs
                df_cat_matched.replace(r'^\s*$', np.nan, regex=True)

                if verbose:
                    print(f'NO DETECTION MATCH FOUND IN {column_ending} CATALOG:', m)

            df_cat_matched = df_cat_matched.reset_index(drop=False)

            df_cattmp[f"MAG_AUTO_{column_ending}"]     = df_cat_matched["MAG_AUTO"]
            df_cattmp[f"MAGERR_AUTO_{column_ending}"]  = df_cat_matched["MAGERR_AUTO"]
            df_cattmp[f"X_WORLD_{column_ending}"]      = df_cat_matched["X_WORLD"]
            df_cattmp[f"Y_WORLD_{column_ending}"]      = df_cat_matched["Y_WORLD"]
            df_cattmp[f"X_IMAGE_{column_ending}"]      = df_cat_matched["X_IMAGE"]
            df_cattmp[f"Y_IMAGE_{column_ending}"]      = df_cat_matched["Y_IMAGE"]
            df_cattmp[f"CLASS_STAR_{column_ending}"]   = df_cat_matched["CLASS_STAR"]
            df_cattmp[f"ELLIPTICITY_{column_ending}"]  = df_cat_matched["ELLIPTICITY"]
            df_cattmp[f"FWHM_WORLD_{column_ending}"]   = df_cat_matched["FWHM_WORLD"]
            df_cattmp[f"FWHM_IMAGE_{column_ending}"]   = df_cat_matched["FWHM_IMAGE"]
            df_cattmp[f"SPREAD_MODEL_{column_ending}"] = df_cat_matched["SPREAD_MODEL"]
            df_cattmp[f"FLAGS_{column_ending}"]        = df_cat_matched["FLAGS"]

        return df_cattmp