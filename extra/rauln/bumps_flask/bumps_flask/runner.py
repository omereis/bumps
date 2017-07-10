from . import app, rdb, rqueue

# note: allow for usage of SLURM scheduler as well as RQ

def run_job():
    pass



def tear_down_job(jobid):
    '''
    Erase a job from DB and call a file deletion function
    TODO: Should be called after a job signals it is completed, perhaps...
    note: should use file_handler for dealing with actual files
    '''
    pass
