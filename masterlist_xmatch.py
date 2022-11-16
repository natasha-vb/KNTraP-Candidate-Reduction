import argparse
import glob
import pandas as pd 
import re

from utils import crossmatch

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Source Extractor to filter transient candidates")
    parser.add_argument(
            "field",
            type=str,
            help="Selected field"
    )
    args = parser.parse_args()

    # Grabbing all masterlists
    if args.field:
        masterlists = glob.glob(f'./masterlist/{args.field}/*.allccds.csv')
    else:
        masterlists = glob.glob('./masterlist/*/*allccds.csv')
    
    for ml in masterlists:

        # Directory path to save xmatched masterlists
        if args.field:
            field = args.field
        else:
            field = re.split(r'[_.]', ml)[2]
        outdir = f'./masterlist{field}'

        # Crossmatching candidates with Simbad, Gaia, and Pan-STARRS 1 catalogues
        ml_file = pd.read_csv(ml)
        
        ml_xmatch = crossmatch.crossmatch(ml_file,verbose=True)
        ml_xmatch.to_csv(f'{outdir}/masterlist_{args.field}.allccds_xmatch.csv', index=False)