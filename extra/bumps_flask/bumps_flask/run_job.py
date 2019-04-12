from . import app, rdb
import multiprocessing
import os
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


# import mpld3

def handle_bumps_script(*args):
    pass


def handle_results():
    pass


def run_job(job):
    from bumps.fitservice import fitservice
    return fitservice(job)


def tear_down_job(job_id):
    '''
    Erase a job from DB and call a file deletion function
    TODO: Should be called after a job signals it is completed, perhaps...
    note: should use file_handler for dealing with actual files
    '''
    pass


def execute_python_script(job_file, args, job_path):
    """
    TEST
    """
    try:
        import traceback
        f = open('debug.txt', 'a')
        f.write("-----------------------------\n")
        f.write("run_job.py-execute_python_script. stack:\n")
        stack = traceback.extract_stack ()
        f.write("Stack length: " + str(len(stack)) + "\n")
        for n in range(len(stack)):
            f.write(str(n+1) + ": " + stack[n])
        for s in stack:
            f.write(str(s) + "\n")
    finally:
        f.close()
    subprocess.Popen(['bumps'] + [job_file] + list(args),
                     cwd=job_path,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)


def execute_slurm_script(cmd, args, job_file, job_path):
    """
    TEST
    """

    """
    """
    try:
        import traceback
        f = open('debug.txt', 'a')
        f.write("-----------------------------\n")
        f.write("run_job.py-execute_slurm_script. stack:\n")
        stack = traceback.extract_stack ()
        f.write("Stack length: " + str(len(stack)) + "\n")
        for n in range(len(stack)):
            f.write(str(n+1) + ": " + str(stack[n]) + "\n")
    finally:
        f.close()
    subprocess.Popen([cmd] + [job_file] + list(args),
                     cwd=job_path,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
