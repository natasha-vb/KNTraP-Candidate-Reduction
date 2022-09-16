import numpy as np

def find_good_detections(det_file):

    # Checking ellipticity requirement (Ellip. < 0.7)
    ell = det_file["ELLIPTICITY_DIFF"]


    # Checking FWHM requirement (FWHM < )


    # Checking Spread Model requirement ()


    ##########################
    # make copy of lc file
    # delete rows of detections which do not meet criteria 
    # find length of file after cuts
    # return this value as number of good detections 
