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
from astropy.visualization import LinearStretch
from astropy.visualization import ZScaleInterval
from astropy.visualization import ImageNormalize


## grab list of primary candidates from ./masterlists/field/priority/primary_candidates_{field}.csv ***might add secondary candidates as an option***
## loop over candidates
## use list to get ccd, ra and dec
## grab fits images (template, science, difference) for all nights matching the candidate
## make cutouts from coordinates of all images (only save 1 template image as these should all be the same --> or save all until after grid created, then delete all but first one)
## save cutouts as .fits files (./lc_files/{field}/filtered_candidates/primary_candidates/thumbnails)
## plot template, science and difference images in a grid, showing evolution over all nights
## save evolution grid as .png

# From Jielai Zhang
def imshow_zscale(image,fits=False,grid=True,ticks=False):
    if fits==True:
        d = fits.getdata(image)
    else:
        d=image
    norm = ImageNormalize(d, interval=ZScaleInterval(),stretch=LinearStretch())
    plt.imshow(d, cmap=plt.cm.gray, norm=norm, interpolation='none')
    if ticks:
        plt.tick_params(labelsize=16)
    if grid:
        plt.grid()
    return None


def make_thumbnail_grid(cand_id, field, primary=False, secondary=False):
    if primary:
        cand_directory = 'primary_candidates'
    if secondary:
        cand_directory = 'secondary_candidates'
    
    # Grab i and g band cutouts 
    i_thumbnails = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*.i.*')
    g_thumbnails = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*.g.*')

    fig, ax = plt.subplots(nrows=3, ncols=11)
    for fits in i_thumbnails:
        imshow_zscale(fits,grid=False,ticks=False)


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


def create_cutout_files(cand_list, field, primary=False, secondary=False, verbose=False):
    # Iterate over masterlist to get candidate data
    for i in range(len(cand_list)):
        cand    = cand_list.iloc[i]
        ra      = cand['RA_AVERAGE']
        dec     = cand['DEC_AVERAGE']
        ccd     = cand['CCD']
        cand_id = cand['CAND_ID']

        print('-------------------------------')
        print(f'Creating thumbnails for candidate {cand_id}')
        print(' ')
        print(f'CCD: {ccd}')
        print(f'RA: {ra}')
        print(f'DEC: {dec}')
        print(' ')
        
        sci_images  = glob.glob(f'../../workspace/{field}_tmpl/{ccd}/*.diff.im.fits')
        diff_images = glob.glob(f'../../workspace/{field}_tmpl/{ccd}/*.diff.fits')
        tmpl_images = glob.glob(f'../../workspace/{field}_tmpl/{ccd}/*.diff.tmpl.fits')

        if verbose:
            print('Images found:')
            print(sci_images)
            print(' ')
            print(diff_images)
            print(' ')
            print(tmpl_images)
            print(' ')

        # Looping over single night images for science, difference, and template images
        images_list = [sci_images, diff_images, tmpl_images]
        for images in images_list:
            for fits in images:
                # Make cutout of candidate
                data, header = create_cutout_centre(fits, ra, dec, 100) # look into image size???

                # Save cutout as .fits to appropriate path
                fits_name = fits.split('/')[-1]
                fits_name = fits.replace(f'.fits', '.cutout.fits')
                candfits_name = 'cand' + cand_id.astype(str) + '_' + fits_name

                print(f'Image thumbnail filename: {candfits_name}')

                if primary:
                    cand_directory = 'primary_candidates'
                if secondary:
                    cand_directory = 'secondary_candidates'

                # Create directory for thumbnail if not already existing
                thumbnail_outdir = (f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails')
                if not os.path.exists(thumbnail_outdir):
                    os.makedirs(thumbnail_outdir)

                fits.writeto(f'{thumbnail_outdir}/{candfits_name}', data, header=header, overwrite=True)

                print(f'Thumbnail saved to: {thumbnail_outdir}')

        # From saved thumbnails, create .png evolution grid of images
        _ = make_thumbnail_grid(cand_id, field=field, primary=primary, secondary=secondary)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create thumbnail images from masterlist of candidates")
    parser.add_argument(
            "field",
            type=str,
            help="Selected field"
    )
    parser.add_argument(
            "--no_primary",
            action="store_true",
            default="store_false",
            help="Do not use primary candidates"
    )
    parser.add_argument(
            "--secondary",
            action="store_true",
            default="store_false",
            help="Use secondary candidates"
    )
    parser.add_argument(
            "--verbose", "--v",
            action="store_true",
            help="Print more information"
    )
    args = parser.parse_args()

    # Grab masterlist of primary/ secondary candidates
    if not args.no_primary:
        m_pri = glob.glob(f'./masterlists/{args.field}/priority/primary_candidates*')
        print('Found masterlist: ', m_pri)

        _ = create_cutout_files(m_pri, args.field, primary=True, verbose=args.verbose)

    if args.secondary:
        m_sec = glob.glob(f'./masterlists/{args.field}/priority/secondary_candidates*')
        print('Found masterlist: ', m_sec)

        _ = create_cutout_files(m_sec, args.field, secondary=True, verbose=args.verbose)

