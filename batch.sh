#!/bin/bash
#SBATCH --cpus-per-task=16 --mem=102400
source ./venv/bin/activate
for ((i=1; i<=17; i++))
do
    python optuna_experiments.py "$i" &
done