from __future__ import absolute_import, unicode_literals
from .celery import app
from bumps import cli
import datetime

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

@app.task
def run_bumps(params):
    return(cli.main(params))
########################################################################################
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
########################################################################################
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
########################################################################################
@app.task
def run_bumps2():
    return(cli.main(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/bumps_flask/results', '--fit=newton']))
