from __future__ import absolute_import, unicode_literals
from .celery import app
from bumps import cli
import datetime
from .sql_db import bumps_sql

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
        file = open(file_path, "w+")
        file.write(file_data)
        file.close()
        print_debug("tasks.py, save_definition_file\ndatabase connected, file saved")
        f = True
    except Exception as e:
        print_debug("tasks.py, save_definition_file\nException: " + str(e))
        f = True
    return (f)
#------------------------------------------------------------------------------
@app.task
def run_bumps(params, job_id, token):
#    print_debug("tasks.py, run_bumps\nparams: " + str(params))
    result = None
    try:
        if (save_definition_file(job_id, token)):
            result = cli.main(params)
    except Exception as e:
        print_debug("tasks.py, run_bumps\nExxception: " + str(e))
    return(result)
#    return(cli.main(params))
#------------------------------------------------------------------------------
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
