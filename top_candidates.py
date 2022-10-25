import glob
import pandas as pd

parser = argparse.ArgumentParser(description="Iterating over candidate filtering conditions")

parser.add_argument(
        "--verbose", "--v",
        action="store_true",
        help="Making code more verbose"
)

masterlists = glob.glob(f'./*/*.allccds_xmatch.csv')

for m in masterlists:

    # Reading in masterlist
    mlist = pd.read_csv(m, sep=',')
    field = mlist['FIELD'][0]

    priority_outdir = (f'./masterlist/{field}/priority')
    if not os.path.exists(priority_outdir):
        os.makedirs(priority_outdir)

    # Separating top tier candidates into a list
    t1_cands = ml_xmatch[lambda ml_xmatch: (ml_xmatch.N_CONSECUTIVE_DETECTIONS_i >= 3) | (ml_xmatch.N_CONSECUTIVE_DETECTIONS_g >= 3) |
                                        (ml_xmatch.N_CONSECUTIVE_DETECTIONS_ig >= 2)] 
    t1_cands = t1_cands.reset_index()
    t1_cands.to_csv(f'{priority_outdir}/tier1_candidates_{args.field}.csv', index=False)

    if args.verbose:
        top_cand_num = len(t1_cands)
        print('')
        print('=================================')
        print(f'TOP {top_cand_num} CANDIDATES IN FIELD {args.field}:')
        print('=================================')
        print(t1_cands[['CAND_ID','CCD','RA_AVERAGE','DEC_AVERAGE','N_CONSECUTIVE_DETECTIONS_i', 'N_CONSECUTIVE_DETECTIONS_g']])
