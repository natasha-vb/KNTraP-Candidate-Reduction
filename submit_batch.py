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

#SBATCH --job-name=JOB_NAME
#SBATCH --output=/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME.out
#SBATCH --error=/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME.err

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=OZSTARWALLTIME
#SBATCH --mem-per-cpu=MEM_REQUESTG
RESERVATION_LINE

echo Slurm Job JOB_NAME start
echo Job bash script is: JOB_BASH_SCRIPT
echo Job .out is saved at: /fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME.out
echo Job .err is saved at: /fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar/FIELDNAME/JOB_NAME.err
echo `date`
SECONDS=0
echo -------- --------
source BASHRCFILE
COMMAND
echo -------- --------
echo `date`
duration=$SECONDS
echo Slurm Job JOB_NAME done in $(($duration / 60)) minutes and $(($duration % 60)) seconds
'''

def submit_slurm_OzSTAR_batch(commandfile,
                                bashrcfile='/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/setup.sourceme',
                                memory_request=8000,
                                verbose=False,
                                do_not_submit=False):
    # Get environment variables for pipeline set up
    pipedata_dir      = '/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction'
    walltime          = os.getenv('OZSTARwalltime')
    if walltime == None:
        walltime='7:00:00'

    # with open(commandfile) as fp:
        pipecommand = commandfile.strip()

        # Define slurm job name
        # Remove full path to "main.py"
        if 'main.py' in pipecommand:
            pipe_command_clean  = pipecommand.split('main.py')[1].strip()

        # Join spaces with _ and replace ' and * and / and < and > and - with nothing
        # replace __ with _
        slurm_job_name      = '_'.join(pipe_command_clean.split(' '))
        slurm_job_name      = slurm_job_name.replace("'",'')
        slurm_job_name      = slurm_job_name.replace("*",'')
        slurm_job_name      = slurm_job_name.replace("/",'')
        slurm_job_name      = slurm_job_name.replace("<",'')
        slurm_job_name      = slurm_job_name.replace(">",'')
        slurm_job_name      = slurm_job_name.replace("-",'')
        slurm_job_name      = slurm_job_name.replace("__",'_')
        slurm_job_name      = slurm_job_name[0:200]

        # when doing websniff, commands are pipeloop and not pipemaster due to batch4amp. To get ccd# in the job name, do this:
        if 'main.py' in pipecommand:
            if len(slurm_job_name.split(',')) > 3:
                slurm_job_name = slurm_job_name.split(',')[0]+',etc,'+slurm_job_name.split(',')[-1]
                slurm_job_name.replace('tmpl_','')

        # This is always the fieldname
        fieldname           = slurm_job_name.split('_')[0]
        print('fieldname:', fieldname)

        # Figure out where to save the slurm script
        slurm_script_dir    = pipedata_dir+f'/logs/ozstar/{fieldname}'
        slurm_script_path   = slurm_script_dir+f'/{slurm_job_name}_slurm.sh'

        # Create output directory if not exist
        just_created  = create_dir_ifnot(slurm_script_dir)
        if just_created == True:
            if verbose == True:
                print(f'VERBOSE/DEBUG: {slurm_script_dir} was just created.')

        # Create slurm batch bash script
        script_string = batch_script_template.replace('JOB_NAME',slurm_job_name)
        script_string = script_string.replace('PIPE_DATA_DIR',pipedata_dir)
        script_string = script_string.replace('COMMAND',pipecommand)
        script_string = script_string.replace('BASHRCFILE',bashrcfile)
        script_string = script_string.replace('FIELDNAME',fieldname)
        script_string = script_string.replace('MEM_REQUEST',str(int(np.ceil(memory_request/1000.))) )
        script_string = script_string.replace('OZSTARWALLTIME',walltime)

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
            'field',
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
            default='/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/setup.sourceme',
            help='Path to bashrc file'
    )
    parser.add_argument(
            '--memory_request',
            default='8000',
            help='Request this much memory'
    )
    args = parser.parse_args()

    ccd = 1

    # Code running mode arguments
    if args.debugmode:
        print(args)
    do_not_submit       = args.do_not_submit
    verbose             = args.verbose
    # Required arguments
    field               = args.field
    commandfile         = f'python main.py --{field} --ccd {ccd} --v --skip_se'
    # Optional arguments (with defaults set)
    bashrcfile          = args.bashrcfile
    memory_request      = int(args.memory_request)

    _ = submit_slurm_OzSTAR_batch(commandfile,
                                bashrcfile=bashrcfile,
                                memory_request = memory_request,
                                verbose=verbose,
                                do_not_submit=do_not_submit)