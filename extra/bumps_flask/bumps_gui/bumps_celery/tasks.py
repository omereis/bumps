from __future__ import absolute_import, unicode_literals
from .celery import app
import bumps.cli
from .res_dir import get_results_directory, run_local_bumps
import sys, os, socket, json
from time import sleep
#------------------------------------------------------------------------------
from .oe_debug import print_debug
#------------------------------------------------------------------------------
@app.task   
def run_bumps(message):
#def run_bumps(client_message):
    #json_message = json.loads(message.replace('\n','\\n'))
    #print(f'json message: {json_message}')
    #res = run_local_bumps (json_message)
    res = run_local_bumps (message)
    return res
#------------------------------------------------------------------------------
@app.task
def add(x, y):
    return x + y
#------------------------------------------------------------------------------
@app.task
def write_file(file_name,file_content):
    try:
        f = open (file_name, 'w')
        f.write(file_content)
        f.close()
        res = f'file {file_name} saved'
    except Exception as e:
        res = f'{e}'
    return (res)
#------------------------------------------------------------------------------
@app.task
def read_bin(file_name):
    try:
        f = open (file_name, 'rb')
        bin_content = f.read()
        f.close()
        file_content = bin_content.hex()
        #res = f'file {file_name} saved'
    except Exception as e:
        res = f'{e}'
    return (file_content)
#------------------------------------------------------------------------------
@app.task
def read_alpha(file_name):
    try:
        f = open (file_name, 'r')
        file_content = f.read()
        f.close()
        #res = f'file {file_name} saved'
    except Exception as e:
        res = f'{e}'
    return (file_content)
#------------------------------------------------------------------------------
