from __future__ import absolute_import, unicode_literals
from .celery import app

@app.task
def bumps_add(x, y):
    return x + y


@app.task
def bumps_mult(x, y):
    return x * y


@app.task
def bumps_xsum(numbers):
    return sum(numbers)
