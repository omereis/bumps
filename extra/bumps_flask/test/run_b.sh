#!/bin/bash

#SBATCH --time=00:30:00
#SBATCH job-name=sfb
#SBATCH --ntasks=2
#SBATCH --mem-per-cpu=512M

python -m bumps.cli ./cf1.py --batch --stepmon --burn=100 --steps=100 --store=./results --fit=newton
