#!/bin/bash

#SBATCH --time=00:30:00
#SBATCH --ntasks=2
#SBATCH --mem-per-cpu=512M

bumps /tmp/bumps_flask/fit_problems/19ab68/job1/curve.py --batch --stepmon --burn=100 --steps=100 --store=/tmp/bumps_flask/fit_problems/19ab68/job1/results --fit=amoeba
