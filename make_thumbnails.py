import argparse
import glob
import matplotlib.pyplot as plt
import numpy as np
import os

import astropy.io.fits as fits
from astropy.nddata import Cutout2D
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord


## grab list of primary candidates from ./masterlists/field/priority/primary_candidates_{field}.csv ***might add secondary candidates as an option***
## loop over candidates
## use list to get ccd, ra and dec
## grab fits images (template, science, difference) for all nights matching the candidate
## make cutouts from coordinates of all images (only save 1 template image as these should all be the same --> or save all until after grid created, then delete all but first one)
## save cutouts as .fits files (./lc_files/{field}/filtered_candidates/primary_candidates/thumbnails)
## plot template, science and difference images in a grid, showing evolution over all nights
## save evolution grid as .png

def make_thumbnail_grid(cand_id, field, primary=False, secondary=False):
    if primary:
        cand_directory = 'primary_candidates'
    if secondary:
        cand_directory = 'secondary_candidates'
    i_thumbnails = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*.i.*')
    g_thumbnails = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*.g.*')


# From Jielai Zhang 
def create_cutout_centre(fitsfile,RA,DEC,image_size,verbose=False,debug=False):
    # Read data
    d,h = fits.getdata(fitsfile,header=True)
    w = WCS(h)
    # Get position in SkyCoords
    pos = SkyCoord(RA, DEC, unit=u.deg)
    # Create cutout
    cutout = Cutout2D(d, size=image_size, position=pos, wcs=w)
    # Create new cutout header with right WCS
    h.update(cutout.wcs.to_header())
    return cutout.data, h

def create_cutout_files(cand_list, field, primary=False, secondary=False):
    # Iterate over masterlist to get candidate data
    for i in range(len(cand_list)):
        cand    = cand_list.iloc[i]
        ra      = cand['RA_AVERAGE']
        dec     = cand['DEC_AVERAGE']
        ccd     = cand['CCD']
        cand_id = cand['CAND_ID']
        
        sci_images = glob.glob(f'../../workspace/{field}_tmpl/{ccd}/*.diff.im.fits')
        diff_images = glob.glob(f'../../workspace/{field}_tmpl/{ccd}/*.diff.fits')
        tmpl_images = glob.glob(f'../../workspace/{field}_tmpl/{ccd}/*.diff.tmpl.fits')

        # Looping over single night images for science, difference, and template images
        images_list = [sci_images, diff_images, tmpl_images]
        for images in images_list:
            for fits in images:
                # Make cutout of candidate
                data, header = create_cutout_centre(i, ra, dec, 100) # look into image size???

                # Save cutout as .fits to appropriate path
                fits_name = fits.split('/')[-1]
                fits_name = fits.replace(f'.fits', '.cutout.fits')
                candfits_name = 'cand' + cand_id.astype(str) + '_' + fits_name
                if primary:
                    cand_directory = 'primary_candidates'
                if secondary:
                    cand_directory = 'secondary_candidates'

                # Create directory for thumbnail if not already existing
                thumbnail_outdir = (f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails')
                if not os.path.exists(thumbnail_outdir):
                    os.makedirs(thumbnail_outdir)

                fits.writeto(f'{thumbnail_outdir}/{candfits_name}', data, header=header, overwrite=True)

        # From saved 
        _ = make_thumbnail_grid(cand_id, field=field, primary=primary, secondary=secondary)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create thumbnail images from masterlist of candidates")
    parser.add_argument(
            "field",
            type=str,
            help="Selected field"
    )
    parser.add_argument(
            "--primary",
            action="store_true",
            help="Use primary candidates"
    )
    parser.add_argument(
            "--secondary",
            action="store_true",
            help="Use secondary candidates"
    )
    args = parser.parse_args()

    # Grab masterlist of primary/ secondary candidates
    if args.primary:
        m_pri = glob.glob(f'./masterlists/{args.field}/priority/primary_candidates*')
        print('Found masterlist: ', m_pri)

        _ = create_cutout_files(m_pri, args.field, primary=True)

    if args.secondary:
        m_sec = glob.glob(f'./masterlists/{args.field}/priority/secondary_candidates*')
        print('Found masterlist: ', m_sec)

        _ = create_cutout_files(m_sec, args.field, secondary=True)
