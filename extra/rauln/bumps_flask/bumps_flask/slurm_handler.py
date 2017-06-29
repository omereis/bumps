#!/usr/bin/env python

import os
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


def parse_commands():
    pass


def build_slurm_script(file_dest, _input):
    '''
    Parse given _input into a slurm script at _output
    '''

    with open(os.path.join(file_dest, 'test.sh'), 'w+') as f:
        f.write('#!/bin/bash\n')
        f.write('#SBATCH {}\n'.format('test'))
        f.write('\n'.join(['{}...{}'.format(key, _input[key]) for key in _input]))


def execute_slurm_script(script):
    '''
    Handle the running of a slurm file
    '''
    subprocess.call([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
