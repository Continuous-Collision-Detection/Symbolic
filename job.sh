#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=96:00:00
#SBATCH --mem=4GB

# Load modules
module purge
module load mathematica/12.1.1
module load python/intel/3.8.6

# Run job
cd <path>
python check_roots.py $1 $2 $3 $4 out <root-folder> --wolfram_kernel_path <mathematica-kernel>
