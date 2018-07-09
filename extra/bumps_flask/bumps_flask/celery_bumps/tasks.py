from __future__ import absolute_import, unicode_literals
from .celery import app
from bumps import cli
import datetime
from .sql_db import bumps_sql, get_current_time_string
from .oe_debug import print_debug
import os
import shutil
#------------------------------------------------------------------------------
@app.task
def add(x, y):
    return x + y
#------------------------------------------------------------------------------
@app.task
def mult(x, y):
    return x * y
#------------------------------------------------------------------------------
@app.task
def xsum(numbers):
    return sum(numbers)
#------------------------------------------------------------------------------
def save_definition_file(job_id, token):
    db = bumps_sql()
    f = False
    try:
        db.connect_to_db()
        file_path, file_data = db.extract_file_and_path(job_id, token)
        if (file_path):
            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            file = open(file_path, "w+")
            file.write(file_data)
            file.close()
            f = True
    except Exception as e:
        print_debug ("Exception in save_definition_file: " + str(e))
        f = False
    return (f)
#------------------------------------------------------------------------------
def get_result_dir_name (params):
    dest = None
    dir_name = None
    for n in range(len(params)):
        if ("--store" in params[n]):
            dest = params[n]
    if (dest):
        try:
            dir_name = dest.split("=")[1]
        except Exception as e:
            print_debug("get_result_dir_name\nException: " + str(e))
    return dir_name
#------------------------------------------------------------------------------
def create_result_dir (params):
    dir_name = get_result_dir_name (params)
    if (dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
#------------------------------------------------------------------------------
@app.task
def run_bumps(params, job_id, token):
    bumps_result = None
    try:
        if (save_definition_file(job_id, token)):
            create_result_dir (params)
            bumps_result = cli.main(params)
            if (bumps_result):
                result_dir = save_results(params, job_id, token)
    except Exception as e:
        print_debug("tasks.py, run_bumps\nExxception: " + str(e))
    return(bumps_result)
#    return(cli.main(params))
#------------------------------------------------------------------------------
def zip_results(job_id, token, result_dir):
    try:
        zip_name = "/tmp/%s_%s" % (token, job_id)
        result_zip_name = shutil.make_archive(zip_name, 'zip', result_dir)
    except Exception as e:
        print_debug ("zip_results exception: " + str(e))
    return (result_zip_name)
#------------------------------------------------------------------------------
def save_results(params, job_id, token):
    try:
        str_end_time = get_current_time_string()
        result_dir = get_result_dir_name (params)
        db = bumps_sql()
        db.connect_to_db()
        zip_name = zip_results(job_id, token, result_dir)
        if (db.save_results (job_id, token, str_end_time, zip_name) == True):
            delete_results_dir(result_dir, zip_name)
    except Exception as e:
        print_debug ("save_results exception: " + str(e))
        result_dir = None
    return result_dir
#------------------------------------------------------------------------------
def  delete_results_dir(result_dir, zip_name):
    try:
        if (result_dir != None):
            shutil.rmtree (result_dir)
        if (zip_name != None):
            os.remove(zip_name)
    except Exception as e:
        print_debug ("tasks.py, delete_results_dir:\nEception: " + str(e))
#------------------------------------------------------------------------------
@app.task
def run_bumps1(params):
    msg = ""
    for n in range(len(params)):
        msg += "params[" + str(n) + "] = '" + str(params[n]) + "\n"
    bumps_params= ['/usr/local/lib/python2.7/dist-packages/bumps/cli.py',\
                    params,\
                    '--batch', '--stepmon', '--burn=100', '--steps=100', \
                     '--store=/home/bumps_user/bumps_flask/results', \
                     '--fit=newton']
   
    return(cli.main(bumps_params))
#------------------------------------------------------------------------------
@app.task
def run_bumps2():
    return(cli.main(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/bumps_flask/results', '--fit=newton']))
#------------------------------------------------------------------------------
@app.task
def run_bumps3(src, dest):
    bumps_params= ['/usr/local/lib/python2.7/dist-packages/bumps/cli.py',\
                    src, \
                    '--batch', '--stepmon', '--burn=100', '--steps=100', \
                    "'--store=" + dest + "'", \
                     '--fit=newton']
    msg = ""
    for n in range(len(bumps_params)):
        msg += "params[" + str(n) + "]: '" + str(bumps_params[n]) + "'\n"
    return(cli.main(bumps_params))
