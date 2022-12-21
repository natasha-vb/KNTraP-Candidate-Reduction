# Code from Jielai Zhang

#!/usr/bin/env python

import argparse
import sys, os
import numpy as np

def create_dir_ifnot(directory):

    if os.path.isdir(directory):
        created_or_not = False
    else:
        os.makedirs(directory)
        created_or_not = True

    return created_or_not

##############################################################
####################### Main Function ########################
##############################################################

batch_script_template = '''#!/bin/bash

#SBATCH --job-name=JOB_NAME1
#SBATCH --output=/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME1.out
#SBATCH --error=/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME1.err

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=OZSTARWALLTIME
#SBATCH --mem-per-cpu=MEM_REQUESTG
RESERVATION_LINE

echo Slurm Job JOB_NAME1 start
echo Job bash script is: JOB_BASH_SCRIPT1
echo Job .out is saved at: /fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME1.out
echo Job .err is saved at: /fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME1.err
echo `date`
SECONDS=0
echo ----------------
source BASHRCFILE
COMMAND1
echo ----------------
echo `date`
duration=$SECONDS
echo Slurm Job JOB_NAME1 done in $(($duration / 60)) minutes and $(($duration % 60)) seconds


#SBATCH --job-name=JOB_NAME2
#SBATCH --output=/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME2.out
#SBATCH --error=/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME2.err

echo Slurm Job JOB_NAME2 start
echo Job bash script is: JOB_BASH_SCRIPT2
echo Job .out is saved at: /fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME2.out
echo Job .err is saved at: /fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME2.err

echo `date`
SECONDS=0
echo ----------------
source BASHRCFILE
COMMAND2
echo ----------------
echo `date`
duration=$SECONDS
echo Slurm Job JOB_NAME2 done in $(($duration / 60)) minutes and $(($duration % 60)) seconds

'''

def submit_slurm_OzSTAR_batch(commandfile, field,
                                bashrcfile='/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/setup.bash.sourceme',
                                memory_request=8000,
                                verbose=False,
                                do_not_submit=False):
    # Get environment variables for pipeline set up
    pipedata_dir      = '/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction'
    walltime          = os.getenv('OZSTARwalltime')
    if walltime == None:
        walltime='5:00:00'

    # with open(commandfile) as fp:
        pipecommand = commandfile.strip()

        # Define slurm job name
        fieldname = field

        if 'top_candidates.py' in pipecommand:
            slurm_job_name = f'{fieldname}_topcandidates'
            NUM = 1

        elif 'make_lightcurves.py' in pipecommand:
            slurm_job_name = f'{fieldname}_make_lightcurves'
            NUM = 2

        # Figure out where to save the slurm script
        slurm_script_dir    = pipedata_dir+f'/logs/ozstar/{fieldname}'
        slurm_script_path   = slurm_script_dir+f'/{slurm_job_name}_slurm.sh'

        # Create output directory if not exist
        just_created  = create_dir_ifnot(slurm_script_dir)
        if just_created == True:
            if verbose == True:
                print(f'VERBOSE/DEBUG: {slurm_script_dir} was just created.')

        # Create slurm batch bash script
        script_string = batch_script_template.replace(f'JOB_NAME{NUM}',slurm_job_name)
        script_string = script_string.replace(f'PIPE_DATA_DIR',pipedata_dir)
        script_string = script_string.replace(f'COMMAND{NUM}',pipecommand)
        script_string = script_string.replace(f'BASHRCFILE',bashrcfile)
        script_string = script_string.replace(f'FIELDNAME',fieldname)
        script_string = script_string.replace(f'MEM_REQUEST',str(int(np.ceil(memory_request/1000.))) )
        script_string = script_string.replace(f'JOB_BASH_SCRIPT{NUM}',slurm_script_path)
        script_string = script_string.replace(f'OZSTARWALLTIME',walltime)

        # Write the bash script to file
        f = open(slurm_script_path,'w')
        f.write(script_string)
        f.close()

        # print
        print(f'Saved  : {slurm_script_path}')

        # submit slurm script
        sbatchcommand = f'sbatch {slurm_script_path}'
        print(f'Running: {sbatchcommand}')
        try:
            os.system(sbatchcommand)
        except:
            sys.exit(f'!!! ERROR-- sys.exit when running: {sbatchcommand}')

    # Finish
    # return None


############################################################################
####################### BODY OF PROGRAM STARTS HERE ########################
############################################################################

if __name__ == "__main__":

    # Read in input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--field',
            type=str,
            help='Selected field'
    )
    parser.add_argument(
            '--debugmode',
            action='store_true',
            help="Activating debug mode"
    )
    parser.add_argument(
            '--verbose', '--v',
            action='store_true',
            help='Print extra info to screen'
    )
    parser.add_argument(
            '--do_not_submit',
            action='store_true',
            help='Do not submit OzSTAR job via batch'
    )
    parser.add_argument(
            '--bashrcfile',
            default='/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPstkrep/candidate_reduction/KNTraP-Candidate-Reduction/setup.bash.sourceme',
            help='Path to bashrc file'
    )
    parser.add_argument(
            '--memory_request',
            default='8000',
            help='Request this much memory'
    )
    args = parser.parse_args()
    
    # Code running mode arguments
    if args.debugmode:
        print(args)
    do_not_submit       = args.do_not_submit
    verbose             = args.verbose
    if args.field:
        field           = args.field

    # Optional arguments (with defaults set)
    bashrcfile          = args.bashrcfile
    memory_request      = int(args.memory_request)

    # Command line for candidate filtering script

    commandfile         = f'python top_candidates.py --field {field} --v'
    _ = submit_slurm_OzSTAR_batch(commandfile, field,
                                    bashrcfile=bashrcfile,
                                    memory_request = memory_request,
                                    verbose=verbose,
                                    do_not_submit=do_not_submit)

    commandfile         = f'python make_lightcurves.py --field {field}'
    _ = submit_slurm_OzSTAR_batch(commandfile, field,
                                    bashrcfile=bashrcfile,
                                    memory_request = memory_request,
                                    verbose=verbose,
                                    do_not_submit=do_not_submit)