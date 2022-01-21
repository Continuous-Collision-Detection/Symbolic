#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=96:00:00
#SBATCH --mem=8GB
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zfergus@nyu.edu

# exit when any command fails
set -e

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command failed with exit code $?."' EXIT

# Load modules
module purge
module load mathematica/12.1.1
module load python/intel/3.8.6

# Run job
cd /home/zjf214/symbolic-ccd
EDGE_EDGE=$1
shift
python save_roots.py ${EDGE_EDGE} -i $@
