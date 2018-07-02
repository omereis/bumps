from __future__ import absolute_import, unicode_literals
from .celery import app
from bumps import cli
import datetime
from .sql_db import bumps_sql
from .oe_debug import print_debug
import os
import zipfile
@app.task
def add(x, y):
    return x + y

'''
@app.task
def mult(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
'''

#------------------------------------------------------------------------------
def save_definition_file(job_id, token):
    db = bumps_sql()
    f = False
    try:
        db.connect_to_db()
        file_path, file_data = db.extract_file_and_path(job_id, token)
        print_debug ("save_definition_file, file_path: " + str(file_path))
        if (file_path):
            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            file = open(file_path, "w+")
            file.write(file_data)
            file.close()
            print_debug ("save_definition_file, file_path: " + str(file_path))
            print_debug ("save_definition_file, file_dir: " + str(file_dir))
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
    print_debug ("tasks.py, create_result_dir\nparams: " + str(params) + "\ntype(params): " + str(type(params)))
    dir_name = get_result_dir_name (params)
    if (dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
#            print_debug ("tasks.py, create_result_dir\ndir_name: " + str(dir_name) + " created")
#------------------------------------------------------------------------------
@app.task
def run_bumps(params, job_id, token):
#    print_debug("tasks.py, run_bumps\nparams: " + str(params))
    result = None
    try:
        print_debug("run_bumps\nparams: " + str(params))
        if (save_definition_file(job_id, token)):
#            print_debug("tasks.py, run_bumps\ndefinition saved")
            create_result_dir (params)
            result = cli.main(params)
#            print_debug("tasks.py, run_bumps\nresult: " + str(result))
#            if (result):
#                save_results(params, job_id, token, result)
    except Exception as e:
        print_debug("tasks.py, run_bumps\nExxception: " + str(e))
    return(result)
#    return(cli.main(params))
#------------------------------------------------------------------------------
def zip_results(job_id, token, result_dir):
    results_zip = "/tmp/%s_%d.zip" % (token, job_id)
    if (os.path.isfile(results_zip)): # file exists
        os.remove (results_zip)
    zip_file = zipfile.ZipFile(results_zip, 'w')
    for root, dirs, files in os.walk(result_dir):
        for file in files:
            zip_file.write(os.path.join(root, file))
    zip_file.close()
    print_debug ("result zip: " + str(results_zip))
    return (results_zip)
#------------------------------------------------------------------------------
def save_results(params, job_id, token, result):
    db = bumps_sql()
#    try:
    db.connect_to_db()
    print_debug ("tasks.py, save_results\nresult: " + str(result))
    zip_results(job_id, token, result_dir)
#        db.update_results(job_id, token, result)
#    return (True)    
#------------------------------------------------------------------------------
def print_debug1(strMessage):
    try:
        f = open ("oe_debug.txt", "a+")
        f.write("\n--------------------------------------------------\n")
        f.write(str(datetime.datetime.now()) + "\n")
        f.write("Message: " + strMessage + "\n")
        f.write("--------------------------------------------------\n")
        f.close()
    finally:
        f.close()
#------------------------------------------------------------------------------
@app.task
def run_bumps1(params):
    print_debug("length(params): " + str(len(params)) + "\n")
    msg = ""
    for n in range(len(params)):
        msg += "params[" + str(n) + "] = '" + str(params[n]) + "\n"
    print_debug(msg)
    bumps_params= ['/usr/local/lib/python2.7/dist-packages/bumps/cli.py',\
                    params,\
                    '--batch', '--stepmon', '--burn=100', '--steps=100', \
                     '--store=/home/bumps_user/bumps_flask/results', \
                     '--fit=newton']
   
#    ['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/bumps_flask/results', '--fit=newton']
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
    print_debug("bumps_params='" + str(bumps_params) + "'\n")
    msg = ""
    for n in range(len(bumps_params)):
        msg += "params[" + str(n) + "]: '" + str(bumps_params[n]) + "'\n"
    print_debug(msg)
#    ['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/bumps_flask/results', '--fit=newton']
    return(cli.main(bumps_params))
