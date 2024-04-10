import argparse
import glob
import pandas as pd 
import re

from utils import crossmatch

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Crossmatch candidates from masterlists to Simbad, Gaia, and Pan-STARRS")
    parser.add_argument(
            "--field",
            type=str,
            help="Selected field"
    )
    parser.add_argument(
            "--skip_ps1",
            action='store_true',
            help="Skip Pan-STARRS crossmatching"
    )
    args = parser.parse_args()

    # Grabbing all masterlists
    if args.field:
        masterlists = glob.glob(f'./masterlist/{args.field}/*.allccds.csv')
    else:
        masterlists = glob.glob('./masterlist/*/*allccds.csv')
    
    print('MASTERLIST/S:')
    print(masterlists)

    for ml in masterlists:
        # Directory path to save xmatched masterlists
        if args.field:
            field = args.field
        else:
            field = re.split(r'[_.]', ml)[2]
        outdir = f'./masterlist/{field}'

        # Crossmatching candidates with Simbad, Gaia, and Pan-STARRS 1 catalogues
        try:
            ml_file = pd.read_csv(ml)
            
            print('Masterlist to be crossmatched:')
            print(ml_file)

            ml_xmatch = crossmatch.crossmatch(ml_file, skip_ps1=args.skip_ps1, verbose=True)
            print('Crossmatching complete!')
            print(' ')

            print('Crossedmatched Masterlist:')
            print(ml_xmatch)

            ml_xmatch.to_csv(f'{outdir}/masterlist_{field}.allccds_xmatch.csv', index=False)
        except:
            print('Masterlist is empty or corrupted:')
            print(ml)