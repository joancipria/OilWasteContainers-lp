#!/bin/bash
#SBATCH --cpus-per-task=30 --mem=92160
source ./venv/bin/activate
for ((i=1; i<=30; i++))
do
    python main.py "$i" &
done