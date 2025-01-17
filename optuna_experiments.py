import optuna
import random
import numpy
from deap import base, creator, tools, algorithms
from ga_functions import (
    eval_fitness,
    feasible,
    distance,
    create_individual_random,
    create_heuristic_individual,
)
from custom_deap import eaSimple

study_name = "ga-random-init-optimization"

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)


def objective(trial):
    # --- Fixed params ---
    not_feasible_penalty = 900000
    ngen = 300  # Number of generations

    # --- Optimisation parameters ---

    # The probability of mutating an individual. From 0.01 to 0.5
    mutation_prob = trial.suggest_float("mutation_prob", 0.01, 0.5, step=0.01)

    # Independent probability for each attribute to be flipped. 0.05 to 0.2,
    indpb_mutate = trial.suggest_float("indpb_mutate", 0.05, 0.3, step=0.01)

    # The probability of mating two individuals.
    crossover_prob = trial.suggest_float("crossover_prob", 0.1, 1, step=0.1)  #

    # Independent probability for each attribute to be exchanged 0.1 to 0.5
    indpb_mate = trial.suggest_float("indpb_mate", 0.1, 0.5, step=0.1)

    population_size = trial.suggest_int("population_size", 100, 1000, step=100)
    tournament_size = trial.suggest_int("tournament_size", 2, 8, step=2)

    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register(
        "individual",
        create_individual_random,
        # tools.initRepeat,
        # creator.Individual,
        # toolbox.attr_bool,
        # individual_size,
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Operators
    toolbox.register("evaluate", eval_fitness)
    toolbox.decorate(
        "evaluate", tools.DeltaPenality(feasible, not_feasible_penalty, distance)
    )
    toolbox.register("mate", tools.cxUniform, indpb=indpb_mate)
    toolbox.register("mutate", tools.mutFlipBit, indpb=indpb_mutate)
    toolbox.register("select", tools.selTournament, tournsize=tournament_size)

    pop = toolbox.population(n=population_size)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = eaSimple(
        pop,
        toolbox,
        crossover_prob,
        mutation_prob,
        ngen,
        stats=stats,
        halloffame=hof,
        verbose=True,
        trial=trial,
        optuna=optuna,
    )
    best_individual = hof.items[0]
    best_fitness = eval_fitness(best_individual)

    best_gen = -1
    for gen, record in enumerate(log):
        if record["min"] == best_fitness[0]:
            best_gen = gen
            break
    return best_fitness


# Set up and run the Optuna study
study = optuna.create_study(
    direction="minimize",
    storage="sqlite:///db.sqlite3",  # Specify the storage URL here.
    study_name=study_name,
    load_if_exists=True,
    pruner=optuna.pruners.HyperbandPruner(),
)
study.optimize(objective, n_trials=600)
