#!/bin/bash
#SBATCH --cpus-per-task=32 --mem=92160
source ./venv/bin/activate
for ((i=1; i<=30; i++))
do
    source ./venv/bin/activate && python main.py "$i" &
done