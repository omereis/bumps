from __future__ import absolute_import, unicode_literals
from .celery import app
import bumps.cli
from .local_fit import get_results_directory, run_local_fit
import sys, os, socket, json
from time import sleep
#------------------------------------------------------------------------------
from .oe_debug import print_debug
#------------------------------------------------------------------------------
@app.task   
def run_bumps(message):
    res = run_local_fit (message)
    return res
#------------------------------------------------------------------------------
@app.task
def add(x, y):
    return x + y
#------------------------------------------------------------------------------
