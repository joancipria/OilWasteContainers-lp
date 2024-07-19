import random
import numpy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from ga_functions import eval_fitness, feasible, max_containers, create_individual_random, create_heuristic_individual
from utils import write_results, get_solution_coords, voronoi_division
from data import possible_locations, valencia_region_polygon
import pickle
import sys

run_id = sys.argv[1]


# --- Parameters ---
not_feasible_penalty = 900000
cxpb = 0.8  # The probability of mating two individuals.
mutpb = 0.18000000000000002  # The probability of mutating an individual.
ngen = 300  # Number of generations
pop_size = 500
tournament_size = 4
indpb_mate = 0.5  # Independent probability for each attribute to be exchanged
indpb_mutate = (
    0.16999999999999998  # Independent probability for each attribute to be flipped.
)

# Types
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initialization
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
toolbox.decorate("evaluate", tools.DeltaPenality(feasible, not_feasible_penalty))
toolbox.register("mate", tools.cxUniform, indpb=indpb_mate)
toolbox.register("mutate", tools.mutFlipBit, indpb=indpb_mutate)
toolbox.register("select", tools.selTournament, tournsize=tournament_size)


def main(pop_size, cxpb, mutpb, ngen):
    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        cxpb,
        mutpb,
        ngen,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )

    with open(f"./results/ga_random_{run_id}.pickle", "wb") as log_file:
        pickle.dump(log, log_file)

    return pop, log, hof


if __name__ == "__main__":
    pop, log, hof = main(pop_size, cxpb, mutpb, ngen)

    best_individual = hof.items[0]
    best_fitness = eval_fitness(hof.items[0])[0]


    solution_coords = get_solution_coords(best_individual, possible_locations)
    voronoi_polygons = voronoi_division(solution_coords, valencia_region_polygon)
    write_results(
        f"ga_random_{run_id}",
        best_fitness,
        best_individual,
        solution_coords,
        voronoi_polygons,
    )
