#!/usr/bin/env python

import os
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


def build_slurm_script(file_dest, _input, _output):
    '''
    Parse given _input into a slurm script at _output
    '''

    with open(file_dest, 'w') as f:
        f.write('#!/bin/sh\n')


def execute_slurm_script(script):
    '''
    Handle the running of a slurm file
    '''
    subprocess.call([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
