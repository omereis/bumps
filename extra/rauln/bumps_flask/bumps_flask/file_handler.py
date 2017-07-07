import os
import sys
import tempfile
from werkzeug.utils import secure_filename

from . import app, rdb, jwt

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


def setup_job(user, _input, _file):
    # Convenient variable
    folder = os.path.join(
        app.config.get('UPLOAD_FOLDER'),
        'fit_problems',
        user)

    # Make sure the upload folder exists beforehand
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Sanitize the filename
    filename = secure_filename(_file.filename)
    # Save the uploaded file
    _file.save(os.path.join(folder, filename))

    # Build the slurm batch script for running the job
    slurm_file = tempfile.NamedTemporaryFile(dir=folder, delete=False)
    # try:
    build_slurm_script(slurm_file, _input['slurm'], _input['cli'], filename)
    # finally:
    slurm_file.close()


def build_slurm_script(_file, slurm_dict, cli_dict, job_file_name):
    '''
    Parse given slurm_dict and cli_dict into a slurm script _file
    '''
    job_file_name = os.path.basename(job_file_name)

    slurm_opts = slurm_commands(slurm_dict)
    _file.write(slurm_opts)

    cli_opts = cli_commands(cli_dict)
    _file.write('\nbumps{} {}\n'.format(cli_opts, job_file_name))


def slurm_commands(slurm_dict):
    '''
    Input: dicionary of key=slurm commands, value=form values
    Output: String containing the commands parsed and ready to be written
    '''

    output_s = '#!/bin/bash\n\n'

    # Handle the commands which are formatted differently
    for key in slurm_dict:
        if key == 'n_gpus':
            output_s += '#SBATCH --gres=gpu:{}\n'.format(slurm_dict[key])

        elif key == 'limit_node':
            output_s += '#SBATCH --nodes=1\n'

        elif key == 'jobname':
            output_s += '#SBATCH -J "{}"\n'.format(slurm_dict[key])

        elif key == '--mem-per-cpu' or key == 'mem_unit':
            # Handle these in the end, since they should be as one in the slurm command
            pass

        else:
            output_s += '#SBATCH {}={}\n'.format(key, slurm_dict[key])

    # Handle the mem-per-cpu and mem_unit here
    output_s += '#SBATCH --mem-per-cpu={}{}\n'.format(
        slurm_dict['--mem-per-cpu'], slurm_dict['mem_unit'])

    return output_s


def cli_commands(cli_dict):
    '''
    TODO: Consider the CLI args which are just switches
    '''

    output_s = ''
    for key in cli_dict:
        output_s += ' --{}={}'.format(key, cli_dict[key])

    return output_s


def execute_slurm_script(script):
    '''
    Handle the running of a slurm file
    '''

    subprocess.call([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def tear_down_job(jobid):
    '''
    Delete the model files, slurm scripts for a given job.
    TODO: Should be called after a job signals it is completed, perhaps...
    '''
    pass
