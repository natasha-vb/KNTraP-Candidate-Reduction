# Script to reduce number of found transient candidates 

import numpy as np
import argparse 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--pointing", type=str, 
                        help="Select pointing")

    parser.add_argument("-c", "--ccd", type=int
                        default=62,
                        help="Select which CCDs to loop through")
                        #need to be able to make selection about which ccds and not just how many
                        #like read in which selected ccds and be able to select a range

    parser.add_argument("-i", "--inputdir", type=str
                        default="    ",
                        help="Input directories to find input candidates")

     parser.add_argument("-o", "--outputdir", type=str
                        default="    ",
                        help="Output directories to save vetted candidates")
