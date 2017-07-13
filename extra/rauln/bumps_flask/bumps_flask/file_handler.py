import os
import sys
import random
import tempfile
from werkzeug.utils import secure_filename

from . import app, rdb, jwt
from .database import BumpsJob
from .run_job import execute_python_script

def setup_job(user, _input, _file, queue='slurm'):
    # Convenient variable
    folder = os.path.join(
        app.config.get('UPLOAD_FOLDER'),
        'fit_problems',
        user)

    # Add the store location to the bumps args
    _input['cli']['store'] = os.path.join(folder, 'results')

    # Toggle batch mode so we don't display interactive plots
    _input['cli']['batch'] = True

    # Make sure the upload and results
    # folders exist beforehand
    if not os.path.exists(folder):
        os.makedirs(_input['cli']['store'])

    # Sanitize the filename
    filename = secure_filename(_file.filename)
    file_path = os.path.join(folder, filename)
    # Save the uploaded file
    _file.save(file_path)

    # Build the slurm batch script for running the job
    if queue == 'slurm':
        # Open a non-volatile named tempfile for for output
        slurm_file = tempfile.NamedTemporaryFile(dir=folder, delete=False)

        build_slurm_script(slurm_file, _input['slurm'], _input['cli'], file_path)

        slurm_file.close()

    elif queue == 'rq':
        pass

    return random.randint(1, 10)  # DEBUG JOB ID


def slurm_commands(slurm_dict):
    '''
    Buils a string to consisting of parsed SLURM commands
    and returns the string for writing to a file.
    '''

    output_s = '#!/bin/bash\n\n'

    # Handle the commands which are formatted differently
    for key in slurm_dict:
        if key == 'n_gpus':
            pass  # DEBUG
            # output_s += '#SBATCH --gres=gpu:{}\n'.format(slurm_dict[key])

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
    Buils a string to consisting of parsed CLI commands
    and returns the string for writing to a file.
    TODO: Consider the CLI args which are just switches (if/else?)
    '''

    output_s = ''
    for key in cli_dict:

        # Handle the toggles
        if key == 'batch':
            output_s += ' --batch'

        # Handle the options
        else:
            output_s += ' --{}={}'.format(key, cli_dict[key])

    return output_s.lstrip()


def build_slurm_script(_file, slurm_dict, cli_dict, file_path):
    '''
    Parse given slurm_dict and cli_dict into a slurm script _file
    '''

    job_file = os.path.basename(file_path)
    job_path = os.path.dirname(file_path)

    # Parse the slurm options and write them
    # on the open _file
    slurm_opts = slurm_commands(slurm_dict)
    _file.write(slurm_opts)

    # Parse the CLI options and write them
    # on the open _file
    cli_opts = cli_commands(cli_dict)
    _file.write('\nbumps {} {}\n'.format(file_path, cli_opts))

    execute_python_script('bumps', cli_opts.split(), job_file, job_path)  # DEBUG
    return
