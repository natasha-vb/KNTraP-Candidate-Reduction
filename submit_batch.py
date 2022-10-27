##############################################################
####################### Main Function ########################
##############################################################

batch_script_template = '''#!/bin/bash

#SBATCH --job-name=JOB_NAME
#SBATCH --output=/PIPE_DATA_DIR/logs/ozstar/FIELDNAME/JOB_NAME.out
#SBATCH --error=/PIPE_DATA_DIR/logs/ozstar/FIELDNAME/JOB_NAME.err

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=OZSTARWALLTIME
#SBATCH --mem-per-cpu=MEM_REQUESTG
RESERVATION_LINE

echo Slurm Job JOB_NAME start
echo Job bash script is: JOB_BASH_SCRIPT
echo Job .out is saved at: /PIPE_DATA_DIR/logs/ozstar/FIELDNAME/JOB_NAME.out
echo Job .err is saved at: /PIPE_DATA_DIR/logs/ozstar/FIELDNAME/JOB_NAME.err
echo `date`
SECONDS=0
echo -------- --------
source BASHRCFILE KNTRAPmode
COMMAND
echo -------- --------
echo `date`
duration=$SECONDS
echo Slurm Job JOB_NAME done in $(($duration / 60)) minutes and $(($duration % 60)) seconds
'''

def submit_slurm_OzSTAR_batch(commandfile,
                                bashrcfile='/fred/oz100/NOAO_archive/KNTraP_Project/src/photpipe/config/DECAMNOAO/YSE/YSE.bash.sourceme',
                                memory_request=8000,
                                verbose=False,
                                do_not_submit=False):
    # Get environment variables for pipeline set up
    pipeproj_name     = os.getenv('PIPENAME')
    bashrcfile = bashrcfile.replace('YSE',pipeproj_name)
    pipedata_dir      = os.getenv('/fred/oz100/NOAO_archive/KNTraP_Project/photpipe/v20.0/DECAMNOAO/KNTraPreprocessed/candidate_reduction/KNTraP-Candidate-Reduction/logs/ozstar')
    submit_via_sbatch = os.getenv('OZSTARSUBMIT')
    kntrap_mode       = os.getenv('KNTRAPmode')
    walltime          = os.getenv('OZSTARwalltime')
    if walltime == None:
        walltime='7:00:00'
    if kntrap_mode == None:
        kntrap_mode = ''
    if submit_via_sbatch == 'True':
        submit_via_sbatch = True
    elif submit_via_sbatch == 'False':
        submit_via_sbatch = False
    else:
        print('WARNING: OZSTARSUBMIT env variable exported to : ',submit_via_sbatch)
        print('WARNING: As a result, submit_via_sbatch set to False, prepared slurm scripts will not be sbatched.')
        submit_via_sbatch = False

    with open(commandfile) as fp:
        pipecommand = fp.readline().strip()
        cnt = 1
        while pipecommand:
            print('==========')
            print(f"Line {cnt} : {pipecommand}")

            # Define slurm job name
            # Remove full path to "pipemaster.pl"
            if 'pipemaster.pl' in pipecommand:
                pipe_command_clean  = pipecommand.split('pipemaster.pl')[1].strip()
            elif 'pipeloop.pl' in pipecommand:
                pipe_command_clean = pipecommand.split('pipeloop.pl')[1].strip()
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
            if 'pipeloop.pl' in pipecommand:
                if len(slurm_job_name.split(',')) > 3:
                    slurm_job_name = slurm_job_name.split(',')[0]+',etc,'+slurm_job_name.split(',')[-1]
                    slurm_job_name.replace('tmpl_','')

            # This is always the fieldname
            fieldname           = pipe_command_clean.split(' ')[1]

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
            script_string = script_string.replace('KNTRAPmode',kntrap_mode)
            script_string = script_string.replace('OZSTARWALLTIME',walltime)


            # Write the bash script to file
            f = open(slurm_script_path,'w')
            f.write(script_string)
            f.close()

            # print
            print(f'Saved  : {slurm_script_path}')

            # submit slurm script
            if do_not_submit == False and submit_via_sbatch == True:
                sbatchcommand = f'sbatch {slurm_script_path}'
                print(f'Running: {sbatchcommand}')
                try:
                    os.system(sbatchcommand)
                except:
                    sys.exit(f'!!! ERROR-- sys.exit when running: {command}')
                print('Note   : If want to switch of submit via sbatch: put "export OZSTARSUBMIT=False"')
            else:
                print('WARNING: sbatch command not carried out as requested. To submit, put "export OZSTARSUBMIT=True"')

            # read in next line
            pipecommand = fp.readline().strip()
            cnt += 1

    # Finish
    return None


############################################################################
####################### BODY OF PROGRAM STARTS HERE ########################
############################################################################

if __name__ == "__main__":

    # Read in input arguments
    arguments           = docopt.docopt(__doc__)
    # Code running mode arguments
    debugmode           = arguments['--debug']
    if debugmode:
        print(arguments)
    verbose             = arguments['--verbose']
    do_not_submit       = arguments['--do_not_submit']
    # Required arguments
    commandfile         = arguments['<commandfile>']
    # Optional arguments (with defaults set)
    bashrcfile          = arguments['--bashrcfile']
    memory_request      = int(arguments['--request_memory'])
    _                   = arguments['--skiplog']

    _ = submit_slurm_OzSTAR_batch(commandfile,
                                bashrcfile=bashrcfile,
                                memory_request = memory_request,
                                verbose=verbose,
                                do_not_submit=do_not_submit)