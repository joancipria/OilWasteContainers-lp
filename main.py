import random
import numpy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from data import individual_size
from ga_functions import eval_fitness, feasible

from loguru import logger

logger.add("./logs/deap_run_{time}.log")

# --- Parameters ---
not_feasible_penalty = 99999999
cxpb = 0.8  # The probability of mating two individuals.
mutpb = 0.2  # The probability of mutating an individual.
ngen = 40  # Number of generations
pop_size = 300
tournament_size = 3
indpb_mate = 0.5  # Independent probability for each attribute to be exchanged
indpb_mutate = 0.05  # Independent probability for each attribute to be flipped.

# Types
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# Initialization
toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register(
    "individual",
    tools.initRepeat,
    creator.Individual,
    toolbox.attr_bool,
    individual_size,
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


if __name__ == "__main__":
    main(pop_size, cxpb, mutpb, ngen)
