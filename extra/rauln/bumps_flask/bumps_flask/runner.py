from . import app, rdb, rqueue
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

# note: allow for usage of SLURM scheduler as well as RQ

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
