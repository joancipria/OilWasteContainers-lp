import optuna
import random
import numpy
from heuristics import max_population_min_overlap_heuristic
from data import possible_locations, individual_size
from ga_functions import max_containers

study_name = "overlap-heuristic"

def objective(trial):

    # --- Optimisation parameters ---
    threshold = trial.suggest_float("threshold", 0, 1, step=0.01)

    minutes = trial.suggest_int("minutes", 5, 10, step=1)

    result = max_population_min_overlap_heuristic(
        possible_locations, individual_size, max_containers, minutes, threshold
    )

    return result[0]


# Set up and run the Optuna study
study = optuna.create_study(
    direction="minimize",
    storage="sqlite:///db.sqlite3",  # Specify the storage URL here.
    study_name=study_name,
    load_if_exists=True,
    pruner=optuna.pruners.HyperbandPruner(),
)
study.optimize(objective, n_trials=600)