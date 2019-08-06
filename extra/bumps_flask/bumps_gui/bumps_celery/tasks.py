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
    res = run_local_bumps (message)
    return res
#------------------------------------------------------------------------------
@app.task
def add(x, y):
    return x + y
#------------------------------------------------------------------------------
