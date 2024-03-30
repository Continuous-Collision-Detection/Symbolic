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

# Input arguments
# $1: Pickle file
# $2: Start index
# $3: End index
# $4: 1 if edge-edge, 0 if vertex-face

# Run job
cd $HOME/symbolic-ccd
if [ -z "$WOLFRAM_KERNEL" ]; then
    WOLFRAM_KERNEL=$(which wolfram)
fi
python scripts/check_roots.py $1 $2 $3 $4 out <root-folder> --wolfram_kernel_path $WOLFRAM_KERNEL
