#!/bin/bash
#SBATCH --job-name=a1                  # Job name
#SBATCH --output=a1_%j.log             # Standard output and error log
#SBATCH --mail-type=NONE               # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=                   # Where to send mail 
#SBATCH --nodes=1                      # Number of nodes (how many compute boxes)
#SBATCH --ntasks=160                   # Number of MPI ranks (nodes*ntasks-per-node)
#SBATCH --ntasks-per-node=160          # How many tasks on each box
#SBATCH --ntasks-per-socket=40         # How many tasks on each socket
#SBATCH --ntasks-per-core=2            # How many tasks on each core
#SBATCH --cpus-per-task=1              # Number of cpus per MPI rank 
#SBATCH --mem-per-cpu=600mb            # Memory per processor
#SBATCH --time=01:05:00                # Time limit hrs:min:sec
 
#cd $SLURM_SUBMIT_DIR
refl1d --batch --mpi model.py --fit=dream --samples=20000 --burn=100 --time=1 --store=`pwd`/a1_out


