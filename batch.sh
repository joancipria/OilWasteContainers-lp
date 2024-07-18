#!/bin/bash
#SBATCH --cpus-per-task=16 --mem=16384
source ./venv/bin/activate
for ((i=1; i<=30; i++))
do
    python main.py "$i" &
done