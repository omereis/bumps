from __future__ import absolute_import, unicode_literals
from .celery import app
from bumps import cli

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
