from . import app, rdb, rqueue
import multiprocessing
import os
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


# import mpld3

# note: allow for usage of SLURM scheduler as well as RQ

def handle_bumps_script(*args):
    pass


def handle_results():
    pass


def run_job(job):
    from bumps.fitservice import fitservice
    return fitservice(job)


def tear_down_job(jobid):
    '''
    Erase a job from DB and call a file deletion function
    TODO: Should be called after a job signals it is completed, perhaps...
    note: should use file_handler for dealing with actual files
    '''
    pass


def execute_slurm_script(cmd, *args):
    """
    Run a slurm command, capturing any errors.
    """
    with subprocess.Popen([cmd] + list(args),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        try:
            stdout, stderr = process.communicate()
        except BaseException:
            raise

    return stdout, stderr

# @job


def execute_python_script(cmd, args, job_file, job_path):
    '''
    TEST
    '''

    out = open(os.path.join(job_path, 'output.txt'), 'w+')

    with subprocess.Popen([cmd] + [job_file] + list(args),
                          shell=False, cwd=job_path,
                          stdout=out,
                          stderr=subprocess.STDOUT) as process:
        try:
            process.communicate()
            # job.meta['output'] = stdout + stderr
        except JobTimeoutException:
            raise
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

            out.close()

    return
