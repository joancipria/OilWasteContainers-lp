#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=10 
#SBATCH --mem=30720

# Activate virtual env
source ./venv/bin/activate

# Run in parallel
for i in {1..10}; do
    srun --exclusive -N1 -n1 python main.py $i &
done

# Wait for all background jobs to finish
Wait

# Deactivate virtual env
deactivate
