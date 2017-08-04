import os
import json
import shutil
import zipfile
import tempfile
import datetime
from werkzeug.utils import secure_filename

from . import app, rdb
from .run_job import execute_python_script, execute_slurm_script


def setup_files(payload, _input, _file, queue='slurm'):

    # Add the store location to the bumps args
    folder = payload['directory']
    _input['cli']['store'] = os.path.join(folder, 'results')

    # Make sure the upload and results
    # folders exist beforehand
    if not os.path.exists(folder):
        os.makedirs(_input['cli']['store'])

    # Sanitize the filename
    filename = secure_filename(_file.filename)
    file_path = os.path.join(folder, filename)
    # Save the uploaded file
    _file.save(file_path)

    # Parse the CLI options
    cli_opts = cli_commands(_input['cli'])

    # Add the filename to the payload
    payload['filebase'] = filename.split('.')[0]

    # Build the slurm batch script for running the job
    if queue == 'slurm':
        # Open a non-volatile named tempfile for for output
        slurm_file = tempfile.NamedTemporaryFile(dir=folder, delete=False)

        build_slurm_script(slurm_file, _input['slurm'], cli_opts, file_path)

        slurm_file.close()

    # Currently only support for slurm is available
    elif queue == 'rq':
        payload = execute_python_script.queue(
            _file, cli_opts.split(), file_path)

    # TODO: Add some info to the job dict here
    return payload


def zip_files(_dir, file_list):
    # Excluce mc and mcmc files
    work_list = [_file for _file in file_list if 'mc' not in _file.split('.')[1]]
    work_dir = os.path.join(_dir, 'results',)
    # Only create the zip file if it does not already exist
    if not os.path.isfile(os.path.join(work_dir, 'results.zip')):
        with zipfile.ZipFile(os.path.join(work_dir, 'job_results.zip'), mode='w') as zip_file:
            for _file in work_list:
                zip_file.write(os.path.join(work_dir, _file), arcname=_file)


def clean_job_files(user, job_id):
    _dir = os.path.join(
        app.config.get('UPLOAD_FOLDER'), 'fit_problems',
                        user, 'job{}'.format(job_id))
    shutil.rmtree(_dir)


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

        elif key == '--mem-per-cpu' or key == 'mem_unit':
            # Handle these in the end, since they should be as one in the slurm
            # command
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

    # Handle the toggles
    # Toggle batch mode so we don't display interactive plots
    output_s += ' --batch'
    # Toggle stepmon so we can get some useful data from each step
    output_s += ' --stepmon'

    for key in cli_dict:

        # Handle the options
        output_s += ' --{}={}'.format(key, cli_dict[key])

    return output_s.lstrip()


def build_slurm_script(_file, slurm_dict, cli_opts, file_path):
    '''
    Parse given slurm_dict and cli_dict into a slurm script _file
    '''

    job_file = os.path.basename(file_path)
    job_path = os.path.dirname(file_path)

    # Parse the slurm options and write them
    # on the open _file
    slurm_opts = slurm_commands(slurm_dict)
    _file.write(slurm_opts)

    # Write the CLI options
    _file.write('\nbumps {} {}\n'.format(file_path, cli_opts))

    execute_slurm_script('bumps', cli_opts.split(),
                         job_file, job_path)

    return


def search_results(path):
    from glob import glob
    possible_ext = ('dat', 'err', 'mon', 'par',
                    'png', 'log', 'mc')

    return [os.path.basename(_file) for _file in
            glob(os.path.join(path, 'results', '*')) if
            os.path.basename(_file).split('.')[1] in possible_ext]


def update_job_info(user):
    '''
    Go through the user's job list and check their status,
    update the database as necessary. Job status is checked
    by attempting to open specific files associated
    with job progress
    '''
    user_jobs = rdb.hvals(user)

    if not user_jobs:
        return

    for job in user_jobs:
        if isinstance(job, bool):
            continue
        try:
            with open(os.path.join(job['directory'], 'results',
                                   '{}-steps.json'.format(job['filebase'])), 'r') as j:
                job['status'] = 'RUNNING'

        except IOError:
            pass

        try:
            with open(os.path.join(job['directory'], 'results',
                                   '{}-model.html'.format(job['filebase'])), 'r') as f:
                job['status'] = 'COMPLETED'
                job['completed'] = datetime.datetime.now().strftime('%c')
        except BaseException:
            pass

        rdb.hset(user, job['_id'], job)

    return True
