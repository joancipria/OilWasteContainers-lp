import random
from genetic_algorithm import (
    generate_random_pop,
    fitness,
    select_parents,
    cross_parents_uniform,
    mutate_solution,
)
from data import solution_size
from loguru import logger

logger.add("./logs/run_{time}.log")


# Params
pop_size = 100
generation_number = 100
parents_number = 50
mutation_rates = [0.001, 0.005, 0.01, 0.05, 0.1]
tournament_size = 5
max_ones = 250

logger.debug(f" -------------")
logger.debug(f" --- Start ---")
logger.debug(f" -------------")

logger.debug(f"Parameters:")
logger.debug(
    f"pop_size: {pop_size}, generation_number: {generation_number}, parents_number: {parents_number}, mutation_rates: {mutation_rates}, tournament_size: {tournament_size}, max_ones: {max_ones}"
)


def genetic_algorithm(
    solution_size,
    pop_size,
    generation_number,
    parents_number,
    mutation_rate,
    tournament_size,
    max_ones,
):
    logger.debug(f"--- GA started ---")
    # Generate initial pop
    population = generate_random_pop(pop_size, solution_size, max_ones)

    # Main loop of the genetic algorithm
    for generation in range(generation_number):

        # Get fitness of current pop
        fitness_poblacion = [fitness(solution) for solution in population]

        # Print the best fitness of current generation
        the_best = min(fitness_poblacion)
        logger.debug(f"Generation {generation + 1} | Best fitness: {the_best}")

        # Select parents
        parents = select_parents(
            population, fitness_poblacion, parents_number, tournament_size
        )

        # Generate new population through crossovers
        new_population = []
        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(parents, 2)
            child1, child2 = cross_parents_uniform(parent1, parent2, max_ones)
            new_population.extend([child1, child2])

        # Ensure that the new stock is correctly sized
        new_population = new_population[:pop_size]

        # Mutate the individuals of the new population
        for individual in new_population:
            mutate_solution(individual, mutation_rate, max_ones)

        # Replace the old population with the new population
        population = new_population

    # Assessing the fitness of the final stock
    fitness_poblacion = [fitness(individuo) for individuo in population]

    # Find and display the best individual from the final population.
    best_solution = population[fitness_poblacion.index(min(fitness_poblacion))]
    logger.debug(f"Best solution: {best_solution} | Fitness: {min(fitness_poblacion)}")
    return min(fitness_poblacion), best_solution


# Test different mutation_rates
results = []
for rate in mutation_rates:
    best_fitness, best_solution = genetic_algorithm(
        solution_size,
        pop_size,
        generation_number,
        parents_number,
        rate,
        tournament_size,
        max_ones,
    )
    results.append((rate, best_fitness))
    logger.debug(f"Mutation rate: {rate} | Best fitness: {best_fitness}")

# Show results
logger.debug(" --- Experiment results ---")
for rate, fitness in results:
    logger.debug(f"Mutation rate: {rate} | Best fitness: {fitness}")
