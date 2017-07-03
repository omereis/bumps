#!/usr/bin/env python

import os
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


def line_handler(_file, _input):
    '''
    TEST function to handle building the line FitProblem script TEST
    '''
    _file.write('\nfrom bumps.names import *\n\n')
    _file.write('''def line(x, m, b=0):\n\treturn m * x + b\n\n''')

    for key in _input:
        _file.write('{} = {}\n'.format(key, _input[key]))

    _file.write('''\nM = Curve(line,x,y,dy,m=2,b=2)\nM.m.range(0,4)\nM.b.range(-5,5)\n''')

    _file.write('\nproblem = FitProblem(M)\n')


def parse_commands(slurm_dict):
    '''
    Input: dicionary of key=slurm commands, value=form values
    Output: String containing the commands parsed and ready to be written
    '''

    output_s = '#!/bin/bash\n\n'

    # Handle the commands which are formatted differently
    for key in slurm_dict:
        print(key)
        if key == 'n_gpus':
            output_s += '#SBATCH --gres=gpu:{}\n'.format(slurm_dict[key])

        elif key == 'limit_node':
            output_s += '#SBATCH --nodes=1\n'

        elif key == 'jobname':
            output_s += '#SBATCH -J "{}"\n'.format(slurm_dict[key])

        elif key == '--mem-per-cpu' or key == 'mem_unit':
            # Handle these in the end, since they should be as one in the slurm command
            pass

        else:
            output_s += '#SBATCH {}={}\n'.format(key, slurm_dict[key])

    # Handle the mem-per-cpu and mem_unit here
    output_s += '#SBATCH --mem-per-cpu={}{}\n'.format(
        slurm_dict['--mem-per-cpu'], slurm_dict['mem_unit'])

    print(output_s)
    return output_s


def build_slurm_script(_file, _input):
    '''
    Parse given _input into a slurm script at _output
    '''

    slurm_commands = parse_commands(_input)
    _file.write(slurm_commands)


def execute_slurm_script(script):
    '''
    Handle the running of a slurm file
    '''
    subprocess.call([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
