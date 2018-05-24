#!/bin/bash

#SBATCH --time=00:30:00
#SBATCH job-name=sfb
#SBATCH --ntasks=2
#SBATCH --mem-per-cpu=512M

#celery -A bumps worker -E -l info -n bumps -Q bumps_queue

#from bumps import cli
#import sys

# sys.argv=['','/home/app_user/bumps_flask/test/cf1.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/app_user/results', '--fit=newton']
# cli.main()

python -m bumps.cli /home/app_user/bumps_flask/test/cf1.py --batch --stepmon --burn=100 --steps=100 --store=/home/app_user/results --fit=newton
