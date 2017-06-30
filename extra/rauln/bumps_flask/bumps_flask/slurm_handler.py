#!/usr/bin/env python

import os
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


def line_handler(f, _input):
    '''
    TEST function to handle building the line FitProblem script TEST
    '''

    f.write('\nfrom bumps.names import *\n\n')
    f.write('''def line(x, m, b=0):\n\treturn m * x + b\n\n''')

    for key in _input:
        f.write('{} = {}\n'.format(key, _input[key]))

    f.write('''\nM = Curve(line,x,y,dy,m=2,b=2)\nM.m.range(0,4)\nM.b.range(-5,5)\n''')

    f.write('\nproblem = FitProblem(M)\n')


def parse_commands(slurm_dict):
    '''
    Input: dicionary of key=slurm commands, value=form values
    Output: String containing the commands parsed and ready to be written
    '''

    output_s = '#!/bin/bash\n\n'

    # Handle the commands which are formatted differently and remove them
    for key in slurm_dict:
        if key == 'n_gpus':
            output_s += '#SBATCH --gres=gpu:{}\n'.format(slurm_dict[key])

        elif key == 'limit_node':
            output_s += '#SBATCH --nodes=1\n'

        elif key == 'jobname':
            output_s += '#SBATCH -J "{}"\n'.format(slurm_dict[key])

        elif key == '--mem-per-cpu' or key == 'mem_unit':
            # Handle these in the end, since they should be as one
            pass

        else:
            output_s += '#SBATCH {}={}\n'.format(key, slurm_dict[key])

    # Handle the mem-per-cpu and mem_unit heres
    output_s += '#SBATCH --mem-per-cpu={}{}\n'.format(
        slurm_dict['--mem-per-cpu'], slurm_dict['mem_unit'])

    return output_s


def build_slurm_script(file_dest, _input):
    '''
    Parse given _input into a slurm script at _output
    '''

    with open(file_dest, 'w+') as f:
        slurm_commands = parse_commands(_input['slurm'])
        f.write(slurm_commands)
        del _input['slurm']

        line_handler(f, _input['line'])  # DEBUG
        # execute_slurm_script(file_dest)  # DEBUG


def execute_slurm_script(script):
    '''
    Handle the running of a slurm file
    '''
    subprocess.call([script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
