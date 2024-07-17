import random
import numpy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from ga_functions import eval_fitness, feasible, max_containers, create_individual

from loguru import logger

logger.add("./logs/run_{time}.log")

# --- Parameters ---
not_feasible_penalty = 900000
cxpb = 0.8  # The probability of mating two individuals.
mutpb = 0.18000000000000002  # The probability of mutating an individual.
ngen = 300  # Number of generations
pop_size = 500
tournament_size = 4
indpb_mate = 0.5  # Independent probability for each attribute to be exchanged
indpb_mutate = 0.16999999999999998  # Independent probability for each attribute to be flipped.

# Types
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initialization
toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register(
    "individual",
    create_individual,
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

    return pop, log, hof


if __name__ == "__main__":
    logger.debug("--------------------")
    logger.debug("---- GA started ----")
    logger.debug("--------------------")
    logger.debug("\n")
    logger.debug(f"--- Params ---")
    logger.debug(
        f"max_containers: {max_containers}, not_feasible_penalty: {not_feasible_penalty}, cxpb: {cxpb}, mutpb: {mutpb}, ngen: {ngen}, pop_size: {pop_size}, tournament_size: {tournament_size}, indpb_mate: {indpb_mate}, indpb_mutate: {indpb_mutate}"
    )
    logger.debug(f"-------------------")

    pop, log, hof = main(pop_size, cxpb, mutpb, ngen)

    logger.debug("--- Final results ---")
    best_individual = hof.items[0]
    best_fitness = eval_fitness(hof.items[0])
    logger.debug(log)
    logger.debug(
        f"Best individual: {best_individual}, Fitness: {best_fitness}, Containers: {best_individual.count(1)}"
    )
