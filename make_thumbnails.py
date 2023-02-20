import argparse
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

import astropy.io.fits as fits
from astropy.nddata import Cutout2D
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.visualization import LinearStretch
from astropy.visualization import ZScaleInterval
from astropy.visualization import ImageNormalize


# From Jielai Zhang 
def create_cutout_centre(fitsfile,RA,DEC,size=50,verbose=False,debug=False):
    # Read data
    d,h = fits.getdata(fitsfile,header=True)
    w = WCS(h)
    # Get position in SkyCoords
    pos = SkyCoord(RA, DEC, unit=u.deg)
    # Create cutout
    cutout = Cutout2D(d, size=size, position=pos, wcs=w)
    # Create new cutout header with right WCS
    h.update(cutout.wcs.to_header())
    return cutout.data, h

# From Jielai Zhang
def make_stamps(RA,DEC,fitsfiles_2Darray,output='stamp.png',labels=False,size=50,debug=False, verbose=False):
    '''fitsfiles_2Darray should be a 2D array that specifies the number of rows and columns in output stamps.
    E.g. [[temp_1.fits,temp_2.fits],[sci_1.fits,sci2.fits],[sub_1.fits,sub_2.fits]] gives 3 rows and 2 columns.
    '''
            
    ##################
    # Set up subplot #
    ##################
    n_rows = np.shape(fitsfiles_2Darray)[0]
    n_cols = np.shape(fitsfiles_2Darray)[1]   

    if args.verbose:
        print(f"cutout shape: {np.shape(fitsfiles_2Darray)}")
        
    # start figure with pixel axis
    fig, axs = plt.subplots(n_rows, n_cols,figsize=(n_cols*5,n_rows*5))
    fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
    
    ##############################
    # Plot one subplot at a time #
    ##############################
    for row in range(n_rows):
        for col in range(n_cols):
                
            # Read in data, get cutout
            cutout,cutout_h = create_cutout_centre(fitsfiles_2Darray[row][col],
                                            RA,DEC,size=size,verbose=debug,debug=debug)
            
            # imshow, with pixel value normalisation
            norm = ImageNormalize(cutout, interval=ZScaleInterval(),stretch=LinearStretch())
            if n_rows == 1 or n_cols == 1:
                axs[max(row,col)].imshow(cutout, norm = norm, cmap='gray') 
            else:
                axs[row, col].imshow(cutout, norm = norm, cmap='gray') 
                
            # labels
            if col == 1 and row == 1:
                axs[row, col].set_ylabel('Template', fontsize=30)
            if col == 1 and row == 2:
                axs[row,col].set_ylabel('Science', fontsize=30)
            if col == 1 and row == 3:
                axs[row,col].set_ylabel('Difference', fontsize=30)
            
            if labels:
                labels = [[220213,220214,220215,220216,220217,220218,220219,220220,220221,220222],
                          ['','','','','','','','','',''],
                          ['','','','','','','','','','']]
                label=labels[row][col]
            else:
                label=''

            if n_rows == 1 or n_cols ==1:
                axs[max(row,col)].set_axis_off()
                axs[max(row,col)].set_title(label, fontsize=30)
            else:
                axs[row, col].set_axis_off()
                axs[row, col].set_title(label, fontsize=30)
                    
    plt.savefig(output)
    plt.close()

    return output

def make_thumbnail_grid(cand_id, ccd, ra, dec, field, outdir, size=50, primary=False, secondary=False, verbose=False):
    if primary:
        cand_directory = f'primary_candidates_test_{field}'
    if secondary:
        cand_directory = f'secondary_candidates_test_{field}'
    
    # Grab i and g band cutouts 
    filters = ['i','g']
    for filt in filters:
        tmpl_thumbnails = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*{filt}.*stk_{ccd}.diff.tmpl.cutout.fits')
        sci_thumbnails  = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*{filt}.*stk_{ccd}.diff.im.cutout.fits')
        diff_thumbnails = glob.glob(f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails/cand{cand_id}*{filt}.*stk_{ccd}.diff.cutout.fits')

        tmpl_thumbnails.sort()
        sci_thumbnails.sort()
        diff_thumbnails.sort()

        thumbnail_array = [tmpl_thumbnails,sci_thumbnails,diff_thumbnails]
        if verbose:
            print(' ')
            print('Thumbnail array:')
            print(thumbnail_array)
            print(' ')

        output_name = f'{outdir}/cand{cand_id}_{filt}_thumbnail_grid.png'
        if verbose:
            print('Output name:', output_name)

        make_stamps(ra, dec, thumbnail_array, output=output_name, labels=True, size=size, verbose=verbose)

        print(f'Thumbnail grid for candidate {cand_id} saved!')
        print('Save location:', output_name)


def create_cutout_files(cand_list, field, size=50, save_fits=False, primary=False, secondary=False, verbose=False):
    # Iterate over masterlist to get candidate data
    for i in range(len(cand_list)):
        cand_list_csv = pd.read_csv(cand_list[i],sep=',', comment='#', header=11, skipinitialspace=True)
        for ii in range(len(cand_list_csv)):
            cand    = cand_list_csv.iloc[ii]
            ra      = cand['RA_AVERAGE']
            dec     = cand['DEC_AVERAGE']
            ccd     = cand['CCD']
            cand_id = cand['CAND_ID']

            print(' ')
            print('------------------------------------------------------------------------------------------------')
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
            if save_fits: 
                images_list = [sci_images, diff_images, tmpl_images]
                for images in images_list:
                    for fitsfile in images:
                        # Make cutout of candidate
                        data, header = create_cutout_centre(fitsfile, ra, dec, size) # look into image size???

                        # Save cutout as .fits to appropriate path
                        fits_name = fitsfile.split('/')[-1]
                        fits_name = fits_name.replace(f'.fits', '.cutout.fits')
                        candfits_name = 'cand' + cand_id.astype(str) + '_' + fits_name

                        if primary:
                            cand_directory = f'primary_candidates_test_{field}'
                        if secondary:
                            cand_directory = f'secondary_candidates_test_{field}'

                        # Create directory for thumbnail if not already existing
                        thumbnail_outdir = (f'./lc_files/{field}/filtered_candidates/{cand_directory}/thumbnails')
                        if not os.path.exists(thumbnail_outdir):
                            os.makedirs(thumbnail_outdir)

                        fits.writeto(f'{thumbnail_outdir}/{candfits_name}', data, header=header, overwrite=True)

                        print(' ')
                        print(f'Thumbnail saved to: {thumbnail_outdir}/{candfits_name}')

            # From saved thumbnails, create .png evolution grid of images
            _ = make_thumbnail_grid(cand_id, ccd, ra, dec, field=field, outdir=thumbnail_outdir, size=size, primary=primary, secondary=secondary, verbose=verbose)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create thumbnail images from masterlist of candidates")
    parser.add_argument(
            "field",
            type=str,
            help="Selected field"
    )
    parser.add_argument(
            "--image_size",
            type=int,
            help="Thumbnail image size"
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
            "--save_fits",
            action="store_true",
            default="store_false",
            help="Save all individual fits thumbnails"
    )
    parser.add_argument(
            "--verbose", "--v",
            action="store_true",
            help="Print more information"
    )
    args = parser.parse_args()

    # Grab masterlist of primary/ secondary candidates
    if not args.no_primary:
        m_pri = glob.glob(f'./masterlist/{args.field}/priority/primary_candidates*')
        print('Found masterlist: ', m_pri)

        _ = create_cutout_files(m_pri, args.field, size=args.image_size, save_fits=args.save_fits, secondary=True, verbose=args.verbose)

    if args.secondary:
        m_sec = glob.glob(f'./masterlist/{args.field}/priority/secondary_candidates*')
        print('Found masterlist: ', m_sec)

        _ = create_cutout_files(m_sec, args.field, size=args.image_size, save_fits=args.save_fits, secondary=True, verbose=args.verbose)