import datetime
from celery import Celery
from flask_jwt_extended import (get_jwt_identity)
import os
#-------------------------------------------------------------------------------
def print_debug(strMessage):
    try:
        f = open ("oe_debug.txt", "a+")
        f.write("\n--------------------------------------------------\n")
        f.write(str(datetime.datetime.now()) + "\n")
        f.write("Message: " + strMessage + "\n")
        f.write("--------------------------------------------------\n")
        f.close()
    finally:
        f.close()
#-------------------------------------------------------------------------------
def print_stack():
    try:
        import traceback
        f = open ("oe_debug.txt", "a+")
        f.write("-----------------------------\n")
        f.write("Printing Stack:\n")
        stack = traceback.extract_stack ()
        f.write("Stack length: " + str(len(stack)) + "\n")
        for n in range(len(stack)):
            f.write(str(n+1) + ": " + str(stack[n]) + "\n")
#        for s in stack:
#            f.write(str(s) + "\n")
    finally:
        f.close()
from .celery_bumps import celery_misc
#-------------------------------------------------------------------------------
def get_celery_queue_names():
    lstQueueNames = []
    appCeleryBumps = Celery('bumps', broker=celery_misc.get_broker_url(), \
                    backend=celery_misc.get_backend_url())
    dictQueues = appCeleryBumps.control.inspect().active_queues()
    if dictQueues:
        for email in dictQueues:
            queue_list = dictQueues[email]
            for n in range(len(queue_list)):
                try:
                    s = dictQueues[email][n]['name']
                except:
                    s = ""
                lstQueueNames.append(s)
    return lstQueueNames
#------------------------------------------------------------------------------
def get_results_dir (upload_folder, job_id, add_results=False):
    dir = os.path.join(upload_folder, 'fit_problems', get_jwt_identity(), 'job' + str(job_id))
    if (add_results):
        dir = os.path.join(dir, 'results')
    return (dir)
#------------------------------------------------------------------------------
class debug_data(object):
    debug_dir = "debug_dir"
#------------------------------------------------------------------------------
